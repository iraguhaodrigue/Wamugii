"""
Course staff tools: the final-exam bank and results, instructor assignment,
and answering students' lesson questions.

Access: ADMIN/STAFF on every course, an INSTRUCTOR on the courses assigned to
them (`get_course_editor`). Assigning instructors is ADMIN only. The
`/instructor` routes give an instructor their own courses and question inbox.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.api.v1.courses import CourseEditor, get_course_editor
from app.crud import course as course_crud
from app.crud import exam as exam_crud
from app.crud import user as user_crud
from app.models.course import Course, ExamQuestionKind, LessonQuestion
from app.models.user import Role, User
from app.schemas.exam import (
    AiDraftRequest,
    AiDraftResponse,
    ExamAttemptAdmin,
    ExamBankSummary,
    ExamQuestionAdmin,
    ExamQuestionWrite,
    ExamSettings,
    ExamSettingsUpdate,
    InstructorAssign,
    InstructorCourseRead,
    InstructorRead,
    LessonAnswerCreate,
    LessonAnswerRead,
    LessonQuestionRead,
    TopicScore,
)
from app.services import ai_drafts, notifications

router = APIRouter(tags=["exams & instructors"])
logger = logging.getLogger(__name__)

AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]
InstructorOnly = Annotated[User, Depends(require_roles(Role.INSTRUCTOR))]


def _course(db: Session, course_id: int) -> Course:
    course = course_crud.get_course(db, course_id)
    if course is None or not course.is_active:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# --- exam bank -------------------------------------------------------------------------


def _bank(db: Session, course: Course) -> ExamBankSummary:
    questions = exam_crud.list_exam_questions(db, course.id)
    counts = {k.value: 0 for k in ExamQuestionKind}
    for q in questions:
        if q.is_active:
            counts[q.kind.value] += 1
    counts["total"] = sum(counts.values())
    return ExamBankSummary(
        settings=ExamSettings.model_validate(course),
        questions=[ExamQuestionAdmin.model_validate(q) for q in questions],
        counts=counts,
        ai_drafting_available=ai_drafts.is_available(),
    )


@router.get("/courses/{course_id}/exam", response_model=ExamBankSummary,
            dependencies=[Depends(get_course_editor)],
            summary="The final-exam rules and question bank (course staff)")
def get_exam_bank(course_id: int, db: DbDep):
    return _bank(db, _course(db, course_id))


@router.put("/courses/{course_id}/exam/settings", response_model=ExamSettings,
            dependencies=[Depends(get_course_editor)],
            summary="Change the final-exam rules (course staff)")
def update_exam_settings(course_id: int, data: ExamSettingsUpdate, db: DbDep):
    course = _course(db, course_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return ExamSettings.model_validate(course)


@router.post("/courses/{course_id}/exam/questions", response_model=list[ExamQuestionAdmin], status_code=201,
             dependencies=[Depends(get_course_editor)],
             summary="Add one or more questions to the exam bank (course staff)")
def add_exam_questions(course_id: int, items: list[ExamQuestionWrite], db: DbDep):
    _course(db, course_id)
    if not items or len(items) > 100:
        raise HTTPException(status_code=422, detail="Send between 1 and 100 questions")
    start = len(exam_crud.list_exam_questions(db, course_id))
    created = [exam_crud.create_exam_question(db, course_id, item, start + i) for i, item in enumerate(items)]
    return [ExamQuestionAdmin.model_validate(q) for q in created]


@router.put("/courses/{course_id}/exam/questions/{question_id}", response_model=ExamQuestionAdmin,
            dependencies=[Depends(get_course_editor)],
            summary="Edit an exam question (course staff)")
def edit_exam_question(course_id: int, question_id: int, data: ExamQuestionWrite, db: DbDep):
    _course(db, course_id)
    q = exam_crud.get_exam_question(db, course_id, question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return ExamQuestionAdmin.model_validate(exam_crud.update_exam_question(db, q, data))


@router.delete("/courses/{course_id}/exam/questions/{question_id}", status_code=204,
               dependencies=[Depends(get_course_editor)],
               summary="Remove an exam question (course staff)")
def remove_exam_question(course_id: int, question_id: int, db: DbDep):
    _course(db, course_id)
    q = exam_crud.get_exam_question(db, course_id, question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")
    exam_crud.delete_exam_question(db, q)
    return Response(status_code=204)


@router.post("/courses/{course_id}/exam/ai-draft", response_model=AiDraftResponse,
             dependencies=[Depends(get_course_editor)],
             summary="Draft exam questions from lesson notes with AI -- nothing is saved (course staff)")
def ai_draft_questions(course_id: int, data: AiDraftRequest, db: DbDep):
    course = _course(db, course_id)
    lessons = course_crud.list_lessons(db, course_id)
    if data.lesson_ids:
        wanted = set(data.lesson_ids)
        lessons = [l for l in lessons if l.id in wanted]
    if not lessons:
        raise HTTPException(status_code=422, detail="Choose at least one lesson with notes")
    try:
        drafts = ai_drafts.draft_questions(
            course.title,
            [(l.module_title or "", l.title, l.content) for l in lessons],
            data.count,
            [k.value for k in data.kinds],
        )
    except ai_drafts.AiDraftError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return AiDraftResponse(
        drafts=drafts,
        note="These are drafts written by AI. Check every question and answer before saving it.",
    )


# --- results ----------------------------------------------------------------------------


@router.get("/courses/{course_id}/exam/attempts", response_model=list[ExamAttemptAdmin],
            dependencies=[Depends(get_course_editor)],
            summary="Every final-exam attempt on a course, with proctoring events (course staff)")
def list_exam_attempts(course_id: int, db: DbDep):
    from app.services import exam as exam_service

    course = _course(db, course_id)
    out: list[ExamAttemptAdmin] = []
    for a in exam_crud.list_attempts_for_course(db, course_id):
        exam_service.expire_if_due(db, a, course)
        read = ExamAttemptAdmin.model_validate(a)
        read.events = list(a.events or [])
        read.topic_scores = [TopicScore(**t) for t in (a.topic_scores or [])]
        if a.client is not None:
            read.student_name = a.client.full_name
            read.student_email = a.client.email
        out.append(read)
    return out


@router.post("/courses/{course_id}/enrollments/{enrollment_id}/exam/extra-attempt",
             dependencies=[Depends(get_course_editor)],
             summary="Give a student one more final-exam attempt (course staff)")
def grant_extra_attempt(course_id: int, enrollment_id: int, db: DbDep):
    _course(db, course_id)
    enrollment = course_crud.get_enrollment(db, enrollment_id)
    if enrollment is None or enrollment.course_id != course_id:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    enrollment.exam_extra_attempts = (enrollment.exam_extra_attempts or 0) + 1
    db.commit()
    return {"enrollment_id": enrollment.id, "exam_extra_attempts": enrollment.exam_extra_attempts}


# --- instructors (admin) -------------------------------------------------------------------


def _instructor_read(row) -> InstructorRead:
    return InstructorRead(
        user_id=row.user_id,
        full_name=row.user.full_name if row.user else "",
        email=row.user.email if row.user else "",
        assigned_at=row.created_at,
    )


@router.get("/courses/{course_id}/instructors", response_model=list[InstructorRead],
            dependencies=[Depends(get_course_editor)],
            summary="Instructors assigned to a course")
def list_instructors(course_id: int, db: DbDep):
    _course(db, course_id)
    return [_instructor_read(r) for r in exam_crud.list_course_instructors(db, course_id)]


@router.post("/courses/{course_id}/instructors", response_model=InstructorRead, status_code=201,
             summary="Assign an instructor by email (ADMIN). A client account becomes an INSTRUCTOR.")
def assign_instructor(course_id: int, data: InstructorAssign, db: DbDep, admin: AdminOnly):
    course = _course(db, course_id)
    user = user_crud.get_by_email(db, data.email.strip().lower()) or user_crud.get_by_email(db, data.email.strip())
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=404,
            detail="No active account uses this email. Ask the instructor to register first, then assign them.",
        )
    if user.role in (Role.ADMIN, Role.STAFF):
        raise HTTPException(status_code=422, detail="Admins and staff already manage every course.")
    if user.role == Role.TEAM_MEMBER:
        raise HTTPException(status_code=422, detail="This is a project team-member account; use a separate account for teaching.")
    if user.role == Role.CLIENT:
        user.role = Role.INSTRUCTOR
        db.commit()
        logger.info("admin %s promoted user %s to INSTRUCTOR", admin.id, user.id)
    row = exam_crud.assign_instructor(db, course.id, user.id)
    notifications.notify_course_assigned(db, course, user)
    db.refresh(row)
    return _instructor_read(row)


@router.delete("/courses/{course_id}/instructors/{user_id}", status_code=204,
               summary="Remove an instructor from a course (ADMIN)")
def unassign_instructor(course_id: int, user_id: int, db: DbDep, admin: AdminOnly):
    _course(db, course_id)
    if not exam_crud.unassign_instructor(db, course_id, user_id):
        raise HTTPException(status_code=404, detail="That person is not an instructor on this course")
    return Response(status_code=204)


# --- lesson Q&A (course staff) ---------------------------------------------------------------


STAFF_ROLES = (Role.ADMIN, Role.STAFF, Role.INSTRUCTOR)


def display_name(user: User | None, *, full: bool) -> str:
    if user is None:
        return "Former member"
    if full or user.role in STAFF_ROLES:
        return user.full_name
    parts = (user.full_name or "Student").split()
    return parts[0] + (f" {parts[-1][0]}." if len(parts) > 1 else "")


def role_label(user: User | None) -> str:
    if user is None:
        return "Student"
    if user.role == Role.INSTRUCTOR:
        return "Instructor"
    if user.role in (Role.ADMIN, Role.STAFF):
        return "WAMUGII team"
    return "Student"


def question_read(db: Session, q: LessonQuestion, *, viewer: User, full_names: bool) -> LessonQuestionRead:
    return LessonQuestionRead(
        id=q.id,
        course_id=q.course_id,
        lesson_id=q.lesson_id,
        lesson_title=q.lesson.title if q.lesson else "",
        body=q.body,
        author_name=display_name(q.author, full=full_names),
        is_mine=q.author_id == viewer.id,
        created_at=q.created_at,
        answered_by_instructor=exam_crud.answered_by_staff(db, q),
        answers=[
            LessonAnswerRead(
                id=a.id,
                body=a.body,
                author_name=display_name(a.author, full=full_names),
                author_role=role_label(a.author),
                created_at=a.created_at,
            )
            for a in q.answers
        ],
    )


@router.get("/courses/{course_id}/questions", response_model=list[LessonQuestionRead],
            summary="Students' lesson questions on a course (course staff)")
def list_course_questions(course_id: int, db: DbDep, viewer: CourseEditor, unanswered: bool = False):
    _course(db, course_id)
    out = [question_read(db, q, viewer=viewer, full_names=True) for q in exam_crud.list_course_questions(db, [course_id])]
    return [q for q in out if not q.answered_by_instructor] if unanswered else out


@router.post("/courses/{course_id}/questions/{question_id}/answers", response_model=LessonQuestionRead, status_code=201,
             summary="Answer a student's lesson question (course staff)")
def answer_question(course_id: int, question_id: int, data: LessonAnswerCreate, db: DbDep, viewer: CourseEditor):
    course = _course(db, course_id)
    q = exam_crud.get_lesson_question(db, question_id)
    if q is None or q.course_id != course_id:
        raise HTTPException(status_code=404, detail="Question not found")
    exam_crud.add_lesson_answer(db, question=q, author_id=viewer.id, body=data.body)
    db.refresh(q)
    notifications.notify_lesson_answer(db, course, q.lesson, q, viewer)
    return question_read(db, q, viewer=viewer, full_names=True)


@router.delete("/courses/{course_id}/questions/{question_id}", status_code=204,
               summary="Hide a lesson question (course staff)")
def hide_question(course_id: int, question_id: int, db: DbDep, viewer: CourseEditor):
    q = exam_crud.get_lesson_question(db, question_id)
    if q is None or q.course_id != course_id:
        raise HTTPException(status_code=404, detail="Question not found")
    exam_crud.hide_lesson_question(db, q)
    return Response(status_code=204)


# --- the instructor's own area -------------------------------------------------------------


@router.get("/instructor/courses", response_model=list[InstructorCourseRead],
            summary="The courses assigned to me (INSTRUCTOR)")
def my_courses(db: DbDep, me: InstructorOnly):
    ids = exam_crud.list_instructor_course_ids(db, me.id)
    out = []
    for c in sorted(exam_crud.course_ids_with_titles(db, ids), key=lambda c: (c.display_order, c.id)):
        out.append(InstructorCourseRead(
            id=c.id,
            title=c.title,
            slug=c.slug,
            status=c.status.value,
            lesson_count=course_crud.count_active_lessons(db, c.id),
            student_count=course_crud.count_students(db, c.id),
            unanswered_questions=exam_crud.count_unanswered(db, c.id),
            exam_question_count=exam_crud.count_active_exam_questions(db, c.id),
        ))
    return out


@router.get("/instructor/questions", response_model=list[LessonQuestionRead],
            summary="Questions from students on all my courses (INSTRUCTOR)")
def my_questions(db: DbDep, me: InstructorOnly, unanswered: bool = Query(False)):
    ids = exam_crud.list_instructor_course_ids(db, me.id)
    out = [question_read(db, q, viewer=me, full_names=True) for q in exam_crud.list_course_questions(db, ids)]
    return [q for q in out if not q.answered_by_instructor] if unanswered else out
