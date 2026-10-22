import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import (
    Course,
    CourseStatus,
    Enrollment,
    EnrollmentStatus,
    Lesson,
    LessonMaterial,
    LessonProgress,
)
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    LessonCreate,
    LessonUpdate,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = _SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or "course"


def _unique_slug(db: Session, base_slug: str, exclude_id: int | None = None) -> str:
    """
    Append -2, -3, ... until the slug is unique.

    Same pattern as the services CRUD -- extracted here rather than imported
    so a change to the services slug rules can't silently alter course slugs.
    """
    slug = base_slug
    suffix = 2
    while True:
        query = select(Course.id).where(Course.slug == slug)
        if exclude_id is not None:
            query = query.where(Course.id != exclude_id)
        if db.scalar(query) is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


# --- course ---------------------------------------------------------------


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def get_course_by_slug(db: Session, slug: str) -> Course | None:
    return db.scalar(select(Course).where(Course.slug == slug))


def list_courses(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    category: str | None = None,
    search: str | None = None,
    status: CourseStatus | None = None,
    include_inactive: bool = False,
) -> list[Course]:
    query = select(Course)
    if not include_inactive:
        query = query.where(Course.is_active.is_(True))
    if status is not None:
        query = query.where(Course.status == status)
    if category:
        query = query.where(Course.category == category)
    if search:
        query = query.where(func.lower(Course.title).contains(search.lower()))
    query = query.order_by(Course.display_order, Course.id).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def list_published_courses(db: Session, **kwargs) -> list[Course]:
    """Catalog view: only PUBLISHED + active, with the same filters as above."""
    return list_courses(db, status=CourseStatus.PUBLISHED, include_inactive=False, **kwargs)


def create_course(db: Session, data: CourseCreate) -> Course:
    base = _slugify(data.slug or data.title)
    slug = _unique_slug(db, base)
    fields = data.model_dump(exclude={"slug"})
    course = Course(**fields, slug=slug)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course: Course, data: CourseUpdate) -> Course:
    updates = data.model_dump(exclude_unset=True)
    if updates.get("slug"):
        updates["slug"] = _unique_slug(db, _slugify(updates["slug"]), exclude_id=course.id)
    else:
        updates.pop("slug", None)
    for field, value in updates.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


def deactivate_course(db: Session, course: Course) -> Course:
    course.is_active = False
    db.commit()
    db.refresh(course)
    return course


def count_published_courses(db: Session) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Course)
            .where(Course.status == CourseStatus.PUBLISHED, Course.is_active.is_(True))
        )
        or 0
    )


# --- lesson ---------------------------------------------------------------


def get_lesson(db: Session, lesson_id: int) -> Lesson | None:
    return db.get(Lesson, lesson_id)


def get_lesson_for_course(db: Session, course_id: int, lesson_id: int) -> Lesson | None:
    """Scoped lookup -- a lesson id from another course reads as missing."""
    return db.scalar(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id)
    )


def list_lessons(
    db: Session, course_id: int, *, include_inactive: bool = False
) -> list[Lesson]:
    query = select(Lesson).where(Lesson.course_id == course_id)
    if not include_inactive:
        query = query.where(Lesson.is_active.is_(True))
    return list(db.scalars(query.order_by(Lesson.display_order, Lesson.id)).all())


def count_active_lessons(db: Session, course_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Lesson)
            .where(Lesson.course_id == course_id, Lesson.is_active.is_(True))
        )
        or 0
    )


def create_lesson(db: Session, course_id: int, data: LessonCreate) -> Lesson:
    lesson = Lesson(course_id=course_id, **data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def update_lesson(db: Session, lesson: Lesson, data: LessonUpdate) -> Lesson:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)
    return lesson


def deactivate_lesson(db: Session, lesson: Lesson) -> Lesson:
    lesson.is_active = False
    db.commit()
    db.refresh(lesson)
    return lesson


# --- lesson materials -----------------------------------------------------


def create_material(
    db: Session,
    *,
    lesson_id: int,
    uploaded_by: int,
    original_filename: str,
    stored_filename: str,
    storage_path: str,
    content_type: str,
    file_size: int,
) -> LessonMaterial:
    material = LessonMaterial(
        lesson_id=lesson_id,
        uploaded_by=uploaded_by,
        original_filename=original_filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        content_type=content_type,
        file_size=file_size,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def get_material(db: Session, material_id: int) -> LessonMaterial | None:
    return db.get(LessonMaterial, material_id)


def get_material_for_lesson(
    db: Session, lesson_id: int, material_id: int
) -> LessonMaterial | None:
    return db.scalar(
        select(LessonMaterial).where(
            LessonMaterial.id == material_id, LessonMaterial.lesson_id == lesson_id
        )
    )


def list_materials(db: Session, lesson_id: int) -> list[LessonMaterial]:
    return list(
        db.scalars(
            select(LessonMaterial)
            .where(LessonMaterial.lesson_id == lesson_id, LessonMaterial.is_active.is_(True))
            .order_by(LessonMaterial.id)
        ).all()
    )


def deactivate_material(db: Session, material: LessonMaterial) -> LessonMaterial:
    material.is_active = False
    db.commit()
    db.refresh(material)
    return material


# --- enrollments ----------------------------------------------------------


def get_enrollment(db: Session, enrollment_id: int) -> Enrollment | None:
    return db.get(Enrollment, enrollment_id)


def get_enrollment_by_invoice(db: Session, invoice_id: int) -> Enrollment | None:
    """
    The link the paid-unlock hook uses: given an invoice that just hit PAID,
    find the enrollment it unlocks. Scoped to active rows -- a cancelled
    enrollment with a lingering invoice link isn't a target.
    """
    return db.scalar(
        select(Enrollment).where(
            Enrollment.invoice_id == invoice_id, Enrollment.is_active.is_(True)
        )
    )


def get_enrollment_for_client(
    db: Session, course_id: int, client_id: int
) -> Enrollment | None:
    """Pair-lookup for enroll/double-enroll checks and the lesson gate."""
    return db.scalar(
        select(Enrollment).where(
            Enrollment.course_id == course_id, Enrollment.client_id == client_id
        )
    )


def list_enrollments_for_client(db: Session, client_id: int) -> list[Enrollment]:
    return list(
        db.scalars(
            select(Enrollment)
            .where(Enrollment.client_id == client_id, Enrollment.is_active.is_(True))
            .order_by(Enrollment.enrolled_at.desc())
        ).all()
    )


def list_enrollments_for_course(db: Session, course_id: int) -> list[Enrollment]:
    return list(
        db.scalars(
            select(Enrollment)
            .where(Enrollment.course_id == course_id, Enrollment.is_active.is_(True))
            .order_by(Enrollment.enrolled_at.desc())
        ).all()
    )


def count_active_enrollments(db: Session) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Enrollment)
            .where(
                Enrollment.status == EnrollmentStatus.ACTIVE,
                Enrollment.is_active.is_(True),
            )
        )
        or 0
    )


def count_pending_enrollments_for_client(db: Session, client_id: int) -> int:
    """Driver for the adaptive client dashboard: do they have any learning at all."""
    return (
        db.scalar(
            select(func.count())
            .select_from(Enrollment)
            .where(
                Enrollment.client_id == client_id,
                Enrollment.is_active.is_(True),
            )
        )
        or 0
    )


def create_enrollment(
    db: Session,
    *,
    course_id: int,
    client_id: int,
    status: EnrollmentStatus,
    invoice_id: int | None = None,
) -> Enrollment:
    enrollment = Enrollment(
        course_id=course_id,
        client_id=client_id,
        status=status,
        invoice_id=invoice_id,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def set_enrollment_status(
    db: Session, enrollment: Enrollment, status: EnrollmentStatus
) -> Enrollment:
    enrollment.status = status
    db.commit()
    db.refresh(enrollment)
    return enrollment


def set_enrollment_invoice(
    db: Session, enrollment: Enrollment, invoice_id: int
) -> Enrollment:
    enrollment.invoice_id = invoice_id
    db.commit()
    db.refresh(enrollment)
    return enrollment


# --- lesson progress ------------------------------------------------------


def mark_lesson_complete(
    db: Session, enrollment_id: int, lesson_id: int
) -> LessonProgress:
    """
    Idempotent: calling twice on the same lesson keeps the first completion
    date, which is the one that matters for a "completed on" column later.
    """
    existing = db.scalar(
        select(LessonProgress).where(
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    if existing is not None:
        return existing
    row = LessonProgress(enrollment_id=enrollment_id, lesson_id=lesson_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def count_completed_lessons(db: Session, enrollment_id: int) -> int:
    """
    Count completions whose lesson is still active -- a lesson soft-deleted
    after the student completed it doesn't inflate progress against the
    smaller current-total denominator.
    """
    return (
        db.scalar(
            select(func.count())
            .select_from(LessonProgress)
            .join(Lesson, Lesson.id == LessonProgress.lesson_id)
            .where(
                LessonProgress.enrollment_id == enrollment_id,
                Lesson.is_active.is_(True),
            )
        )
        or 0
    )


def progress_percent(completed: int, total: int) -> int:
    """Integer percentage. 0% when there's nothing to complete yet."""
    if total <= 0:
        return 0
    return int(round(100 * completed / total))
