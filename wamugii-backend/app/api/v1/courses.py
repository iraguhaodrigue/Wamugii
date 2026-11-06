"""
Training courses: public catalogue, admin/staff management, lesson materials.

Three layers in this one file so the routes stay together:

* Public catalogue -- `/courses` and `/courses/{slug}` -- open to anyone.
  Only PUBLISHED + active courses are served; the detail serves lesson
  TITLES, never content, since that's gated behind an active enrollment.
* Admin/staff management -- CRUD on courses, lessons and lesson materials.
  Follows the existing convention: STAFF manage, ADMIN deletes.
* The client-facing enrollment + lesson endpoints live in `api/v1/client.py`
  so the "/client" prefix stays one router, matching every other client
  surface.
"""

import logging
from pathlib import Path as PathLib
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, DbDep, OptionalUser, require_roles
from app.core.config import settings
from app.crud import course as course_crud
from app.models.course import Course, CourseStatus, Lesson
from app.models.user import Role, User
from app.schemas.course import (
    CourseCreate,
    CoursePublicDetail,
    CourseRead,
    CourseUpdate,
    EnrollmentRead,
    LessonBrief,
    LessonCreate,
    LessonMaterialRead,
    LessonRead,
    LessonUpdate,
    QuizQuestionAdmin,
    QuizQuestionWrite,
)
from app.services import storage

router = APIRouter(prefix="/courses", tags=["courses"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]


def get_course_editor(course_id: int, db: DbDep, current_user: ActiveUser) -> User:
    """
    ADMIN / STAFF on any course; an INSTRUCTOR only on the courses an admin
    assigned to them. Everyone else gets a 403. Used for lesson content,
    materials, quizzes, the exam bank, students' results and lesson Q&A --
    never for price, publishing or deleting a course.
    """
    from app.crud import exam as exam_crud

    if current_user.role in (Role.ADMIN, Role.STAFF):
        return current_user
    if current_user.role == Role.INSTRUCTOR and exam_crud.is_course_instructor(db, course_id, current_user.id):
        return current_user
    raise HTTPException(status_code=403, detail="You are not an instructor on this course.")


CourseEditor = Annotated[User, Depends(get_course_editor)]

# PDF-first, same tight list as project files. Matched case-insensitively.
MATERIAL_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".zip", ".txt"}


def _is_staff(user: User | None) -> bool:
    return user is not None and user.role in (Role.ADMIN, Role.STAFF)


def _course_read(course: Course, lesson_count: int | None = None) -> CourseRead:
    """Hydrate the computed lesson_count without pulling the whole lesson list."""
    data = CourseRead.model_validate(course)
    data.lesson_count = (
        lesson_count if lesson_count is not None else len([l for l in course.lessons if l.is_active])
    )
    return data


def _public_course_detail(db: Session, course: Course) -> CoursePublicDetail:
    lessons = course_crud.list_lessons(db, course.id)
    detail = CoursePublicDetail.model_validate(course)
    detail.lesson_count = len(lessons)
    detail.lessons = []
    for l in lessons:
        brief = LessonBrief.model_validate(l)
        brief.has_video = bool(l.video_url)
        detail.lessons.append(brief)
    detail.student_count = course_crud.count_students(db, course.id)
    detail.total_minutes = sum(l.duration_minutes or 0 for l in lessons)
    return detail


# --- public catalogue ------------------------------------------------------


@router.get(
    "",
    response_model=list[CourseRead],
    summary="List published courses (public)",
)
def list_public_courses(
    db: DbDep,
    current_user: OptionalUser,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = None,
    search: str | None = None,
    include_drafts: bool = False,
):
    """
    Open endpoint. `include_drafts` is honoured only for staff, same shape as
    `services.list_services` -- a draft course is invisible to the public.
    """
    if include_drafts and _is_staff(current_user):
        courses = course_crud.list_courses(
            db, limit=limit, offset=offset, category=category, search=search,
            include_inactive=True,
        )
    else:
        courses = course_crud.list_published_courses(
            db, limit=limit, offset=offset, category=category, search=search,
        )
    counts = course_crud.active_lesson_counts(db, [c.id for c in courses])
    return [_course_read(c, counts.get(c.id, 0)) for c in courses]


@router.get(
    "/{slug}",
    response_model=CoursePublicDetail,
    summary="Get a published course with its lesson titles (public)",
)
def get_public_course(slug: str, db: DbDep, current_user: OptionalUser):
    """
    Lesson titles only -- `content` and `video_url` live behind the enrollment
    gate at `/client/courses/{id}/lessons/{lesson_id}`, so a visitor browsing
    the catalogue sees the shape of the course but not its material.

    A draft course is a 404 for anyone but staff, matching `get_service`.
    """
    course = course_crud.get_course_by_slug(db, slug)
    if not course or not course.is_active:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.status != CourseStatus.PUBLISHED and not _is_staff(current_user):
        raise HTTPException(status_code=404, detail="Course not found")
    return _public_course_detail(db, course)


# --- admin / staff: courses ------------------------------------------------


def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = course_crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


def _get_lesson_or_404(db: Session, course_id: int, lesson_id: int) -> Lesson:
    lesson = course_crud.get_lesson_for_course(db, course_id, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.post(
    "",
    response_model=CourseRead,
    status_code=201,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
    summary="Create a course (ADMIN or STAFF)",
)
def create_course(data: CourseCreate, db: DbDep):
    course = course_crud.create_course(db, data)
    logger.info("course %s created: %s", course.id, course.title)
    return _course_read(course, 0)


@router.get(
    "/by-id/{course_id}",
    response_model=CourseRead,
    dependencies=[Depends(get_course_editor)],
    summary="Get a course by id for management (ADMIN or STAFF)",
)
def get_course_by_id(course_id: int, db: DbDep):
    """
    By-id lookup for the admin edit screen -- the public endpoint is by slug,
    which can change, so management needs a stable handle. Prefixed `/by-id`
    so the matcher never confuses it with the public `/courses/{slug}`.
    """
    return _course_read(_get_course_or_404(db, course_id))


@router.patch(
    "/{course_id}",
    response_model=CourseRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
    summary="Update a course (ADMIN or STAFF)",
)
def update_course(course_id: int, data: CourseUpdate, db: DbDep):
    """
    `is_free` / `price` have to stay coherent after a partial update, so the
    merged pair is checked against the full create schema before anything is
    written.
    """
    course = _get_course_or_404(db, course_id)

    sent = data.model_dump(exclude_unset=True)
    merged = {
        "title": sent.get("title", course.title),
        "description": sent.get("description", course.description),
        "cover_image_url": sent.get("cover_image_url", course.cover_image_url),
        "category": sent.get("category", course.category),
        "is_free": sent.get("is_free", course.is_free),
        "price": sent["price"] if "price" in sent else course.price,
        "status": sent.get("status", course.status),
        "display_order": sent.get("display_order", course.display_order),
    }
    try:
        CourseCreate.model_validate(merged)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    updated = course_crud.update_course(db, course, data)
    logger.info("course %s updated: %s", course_id, sent)
    return _course_read(updated)


@router.delete(
    "/{course_id}",
    response_model=CourseRead,
    dependencies=[Depends(require_roles(Role.ADMIN))],
    summary="Soft-delete a course (ADMIN only)",
)
def deactivate_course(course_id: int, db: DbDep):
    course = _get_course_or_404(db, course_id)
    updated = course_crud.deactivate_course(db, course)
    logger.info("course %s deactivated", course_id)
    return _course_read(updated)


# --- admin / staff: lessons ------------------------------------------------


@router.get(
    "/{course_id}/lessons",
    response_model=list[LessonRead],
    dependencies=[Depends(get_course_editor)],
    summary="List all lessons on a course for management (ADMIN or STAFF)",
)
def list_course_lessons(course_id: int, db: DbDep, include_inactive: bool = True):
    _get_course_or_404(db, course_id)
    lessons = course_crud.list_lessons(db, course_id, include_inactive=include_inactive)
    out: list[LessonRead] = []
    for lesson in lessons:
        materials = course_crud.list_materials(db, lesson.id)
        read = LessonRead.model_validate(lesson)
        read.materials = [LessonMaterialRead.model_validate(m) for m in materials]
        read.quiz_question_count = course_crud.count_quiz_questions(db, lesson.id)
        out.append(read)
    return out


@router.get(
    "/{course_id}/lessons/{lesson_id}/quiz",
    response_model=list[QuizQuestionAdmin],
    dependencies=[Depends(get_course_editor)],
    summary="A lesson's quiz with answers (ADMIN or STAFF)",
)
def get_lesson_quiz_admin(course_id: int, lesson_id: int, db: DbDep):
    _get_course_or_404(db, course_id)
    _get_lesson_or_404(db, course_id, lesson_id)
    return [QuizQuestionAdmin.model_validate(q) for q in course_crud.list_quiz_questions(db, lesson_id)]


@router.put(
    "/{course_id}/lessons/{lesson_id}/quiz",
    response_model=list[QuizQuestionAdmin],
    dependencies=[Depends(get_course_editor)],
    summary="Replace a lesson's quiz (ADMIN or STAFF); an empty list removes it",
)
def replace_lesson_quiz(
    course_id: int, lesson_id: int, items: list[QuizQuestionWrite], db: DbDep
):
    _get_course_or_404(db, course_id)
    _get_lesson_or_404(db, course_id, lesson_id)
    questions = course_crud.replace_quiz_questions(db, lesson_id, items)
    logger.info("quiz on lesson %s replaced (%s questions)", lesson_id, len(questions))
    return [QuizQuestionAdmin.model_validate(q) for q in questions]


@router.post(
    "/{course_id}/lessons",
    response_model=LessonRead,
    status_code=201,
    dependencies=[Depends(get_course_editor)],
    summary="Add a lesson to a course (ADMIN or STAFF)",
)
def create_lesson(course_id: int, data: LessonCreate, db: DbDep):
    _get_course_or_404(db, course_id)
    lesson = course_crud.create_lesson(db, course_id, data)
    logger.info("lesson %s added to course %s", lesson.id, course_id)
    read = LessonRead.model_validate(lesson)
    read.materials = []
    return read


@router.patch(
    "/{course_id}/lessons/{lesson_id}",
    response_model=LessonRead,
    dependencies=[Depends(get_course_editor)],
    summary="Edit a lesson (ADMIN or STAFF)",
)
def update_lesson(course_id: int, lesson_id: int, data: LessonUpdate, db: DbDep):
    _get_course_or_404(db, course_id)
    lesson = _get_lesson_or_404(db, course_id, lesson_id)
    updated = course_crud.update_lesson(db, lesson, data)
    read = LessonRead.model_validate(updated)
    read.materials = [
        LessonMaterialRead.model_validate(m) for m in course_crud.list_materials(db, updated.id)
    ]
    return read


@router.delete(
    "/{course_id}/lessons/{lesson_id}",
    response_model=LessonRead,
    dependencies=[Depends(require_roles(Role.ADMIN))],
    summary="Soft-delete a lesson (ADMIN only)",
)
def deactivate_lesson(course_id: int, lesson_id: int, db: DbDep):
    _get_course_or_404(db, course_id)
    lesson = _get_lesson_or_404(db, course_id, lesson_id)
    updated = course_crud.deactivate_lesson(db, lesson)
    read = LessonRead.model_validate(updated)
    read.materials = []
    return read


# --- admin / staff: lesson materials --------------------------------------


@router.post(
    "/{course_id}/lessons/{lesson_id}/materials",
    response_model=LessonMaterialRead,
    status_code=201,
    summary="Upload a PDF/doc to a lesson (ADMIN or STAFF)",
)
def upload_lesson_material(
    course_id: int,
    lesson_id: int,
    db: DbDep,
    current_user: CourseEditor,
    file: UploadFile = File(...),
):
    _get_course_or_404(db, course_id)
    lesson = _get_lesson_or_404(db, course_id, lesson_id)

    extension = PathLib(file.filename or "").suffix.lower()
    if extension not in MATERIAL_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type {extension or '(none)'}; allowed: {sorted(MATERIAL_EXTENSIONS)}",
        )

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    try:
        stored_filename, storage_path, file_size = storage.save_lesson_material(
            file.file, lesson.id, extension, max_size_bytes
        )
    except storage.FileTooLargeError:
        raise HTTPException(
            status_code=413, detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit"
        )

    material = course_crud.create_material(
        db,
        lesson_id=lesson.id,
        uploaded_by=current_user.id,
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
    )
    logger.info("material %s uploaded to lesson %s", material.id, lesson.id)
    return material


@router.delete(
    "/{course_id}/lessons/{lesson_id}/materials/{material_id}",
    response_model=LessonMaterialRead,
    dependencies=[Depends(get_course_editor)],
    summary="Soft-delete a lesson material (ADMIN or STAFF)",
)
def deactivate_lesson_material(
    course_id: int, lesson_id: int, material_id: int, db: DbDep
):
    _get_course_or_404(db, course_id)
    _get_lesson_or_404(db, course_id, lesson_id)
    material = course_crud.get_material_for_lesson(db, lesson_id, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return course_crud.deactivate_material(db, material)


# --- admin: enrollments on a course ---------------------------------------


@router.get(
    "/{course_id}/enrollments",
    response_model=list[EnrollmentRead],
    dependencies=[Depends(get_course_editor)],
    summary="List enrollments on a course with progress (ADMIN or STAFF)",
)
def list_course_enrollments(course_id: int, db: DbDep):
    course = _get_course_or_404(db, course_id)
    total = course_crud.count_active_lessons(db, course.id)
    enrollments = course_crud.list_enrollments_for_course(db, course.id)
    out: list[EnrollmentRead] = []
    from app.crud import exam as exam_crud
    from app.models.course import ExamAttemptStatus

    for enrollment in enrollments:
        completed = course_crud.count_completed_lessons(db, enrollment.id)
        read = EnrollmentRead.model_validate(enrollment)
        read.completed_lessons = completed
        read.total_lessons = total
        read.progress_percent = course_crud.progress_percent(completed, total)
        if enrollment.client is not None:
            read.student_name = enrollment.client.full_name
            read.student_email = enrollment.client.email
        read.quizzes_passed = len(course_crud.passed_quiz_lesson_ids(db, enrollment.id))
        attempts = [
            a for a in exam_crud.list_attempts_for_enrollment(db, enrollment.id)
            if a.status == ExamAttemptStatus.SUBMITTED
        ]
        read.exam_attempts = len(attempts)
        read.exam_best_percent = max((a.percent for a in attempts if a.percent is not None), default=None)
        read.exam_passed = any(a.passed for a in attempts)
        read.exam_extra_attempts = enrollment.exam_extra_attempts or 0
        out.append(read)
    return out
