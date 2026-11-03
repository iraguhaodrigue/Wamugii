"""Data access for final exams, course instructors and lesson Q&A."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import (
    Course,
    CourseInstructor,
    ExamAttempt,
    ExamAttemptStatus,
    ExamQuestion,
    LessonAnswer,
    LessonQuestion,
)
from app.models.user import Role, User
from app.schemas.exam import ExamQuestionWrite


# --- instructors ---------------------------------------------------------------


def is_course_instructor(db: Session, course_id: int, user_id: int) -> bool:
    return (
        db.scalar(
            select(CourseInstructor.id).where(
                CourseInstructor.course_id == course_id, CourseInstructor.user_id == user_id
            )
        )
        is not None
    )


def list_course_instructors(db: Session, course_id: int) -> list[CourseInstructor]:
    return list(
        db.scalars(
            select(CourseInstructor)
            .where(CourseInstructor.course_id == course_id)
            .order_by(CourseInstructor.id)
        ).all()
    )


def list_instructor_course_ids(db: Session, user_id: int) -> list[int]:
    return list(
        db.scalars(select(CourseInstructor.course_id).where(CourseInstructor.user_id == user_id)).all()
    )


def assign_instructor(db: Session, course_id: int, user_id: int) -> CourseInstructor:
    row = db.scalar(
        select(CourseInstructor).where(
            CourseInstructor.course_id == course_id, CourseInstructor.user_id == user_id
        )
    )
    if row is None:
        row = CourseInstructor(course_id=course_id, user_id=user_id)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def unassign_instructor(db: Session, course_id: int, user_id: int) -> bool:
    row = db.scalar(
        select(CourseInstructor).where(
            CourseInstructor.course_id == course_id, CourseInstructor.user_id == user_id
        )
    )
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def instructors_for_course(db: Session, course_id: int) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .join(CourseInstructor, CourseInstructor.user_id == User.id)
            .where(CourseInstructor.course_id == course_id, User.is_active.is_(True))
        ).all()
    )


# --- exam questions --------------------------------------------------------------


def list_exam_questions(db: Session, course_id: int, *, active_only: bool = False) -> list[ExamQuestion]:
    stmt = select(ExamQuestion).where(ExamQuestion.course_id == course_id)
    if active_only:
        stmt = stmt.where(ExamQuestion.is_active.is_(True))
    return list(db.scalars(stmt.order_by(ExamQuestion.display_order, ExamQuestion.id)).all())


def count_active_exam_questions(db: Session, course_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(ExamQuestion.id)).where(
                ExamQuestion.course_id == course_id, ExamQuestion.is_active.is_(True)
            )
        )
        or 0
    )


def get_exam_question(db: Session, course_id: int, question_id: int) -> ExamQuestion | None:
    q = db.get(ExamQuestion, question_id)
    return q if q is not None and q.course_id == course_id else None


def create_exam_question(db: Session, course_id: int, data: ExamQuestionWrite, order: int = 0) -> ExamQuestion:
    q = ExamQuestion(course_id=course_id, display_order=order, **data.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def update_exam_question(db: Session, q: ExamQuestion, data: ExamQuestionWrite) -> ExamQuestion:
    for key, value in data.model_dump().items():
        setattr(q, key, value)
    db.commit()
    db.refresh(q)
    return q


def delete_exam_question(db: Session, q: ExamQuestion) -> None:
    """Questions already used in attempts are hidden, not deleted, so old results stay readable."""
    used = db.scalar(select(func.count(ExamAttempt.id)).where(ExamAttempt.course_id == q.course_id))
    if used:
        q.is_active = False
    else:
        db.delete(q)
    db.commit()


def replace_exam_bank(db: Session, course_id: int, items: list[ExamQuestionWrite]) -> int:
    """
    Make the bank match `items` (the content loader). Existing questions with
    the same text are updated in place; the rest are deactivated, never
    deleted, because past attempts point at them.
    """
    existing = {q.question: q for q in list_exam_questions(db, course_id)}
    keep: set[int] = set()
    for order, item in enumerate(items):
        q = existing.get(item.question)
        data = item.model_dump()
        if q is None:
            q = ExamQuestion(course_id=course_id, display_order=order, **data)
            db.add(q)
            db.flush()
        else:
            for key, value in data.items():
                setattr(q, key, value)
            q.display_order = order
            q.is_active = True
        keep.add(q.id)
    for q in existing.values():
        if q.id not in keep:
            q.is_active = False
    db.commit()
    return len(keep)


# --- attempts ------------------------------------------------------------------------


def get_attempt(db: Session, attempt_id: int) -> ExamAttempt | None:
    return db.get(ExamAttempt, attempt_id)


def list_attempts_for_enrollment(db: Session, enrollment_id: int) -> list[ExamAttempt]:
    return list(
        db.scalars(
            select(ExamAttempt)
            .where(ExamAttempt.enrollment_id == enrollment_id)
            .order_by(ExamAttempt.id)
        ).all()
    )


def list_attempts_for_course(db: Session, course_id: int) -> list[ExamAttempt]:
    return list(
        db.scalars(
            select(ExamAttempt)
            .where(ExamAttempt.course_id == course_id)
            .order_by(ExamAttempt.id.desc())
        ).all()
    )


def in_progress_attempt(db: Session, enrollment_id: int) -> ExamAttempt | None:
    return db.scalar(
        select(ExamAttempt).where(
            ExamAttempt.enrollment_id == enrollment_id,
            ExamAttempt.status == ExamAttemptStatus.IN_PROGRESS,
        )
    )


def best_passed_attempt(db: Session, enrollment_id: int) -> ExamAttempt | None:
    return db.scalar(
        select(ExamAttempt)
        .where(ExamAttempt.enrollment_id == enrollment_id, ExamAttempt.passed.is_(True))
        .order_by(ExamAttempt.percent.desc())
        .limit(1)
    )


# --- lesson Q&A -------------------------------------------------------------------------


def list_lesson_questions(db: Session, lesson_id: int) -> list[LessonQuestion]:
    return list(
        db.scalars(
            select(LessonQuestion)
            .where(LessonQuestion.lesson_id == lesson_id, LessonQuestion.is_active.is_(True))
            .order_by(LessonQuestion.id.desc())
        ).all()
    )


def list_course_questions(db: Session, course_ids: list[int]) -> list[LessonQuestion]:
    if not course_ids:
        return []
    return list(
        db.scalars(
            select(LessonQuestion)
            .where(LessonQuestion.course_id.in_(course_ids), LessonQuestion.is_active.is_(True))
            .order_by(LessonQuestion.id.desc())
        ).all()
    )


def get_lesson_question(db: Session, question_id: int) -> LessonQuestion | None:
    q = db.get(LessonQuestion, question_id)
    return q if q is not None and q.is_active else None


def create_lesson_question(db: Session, *, course_id: int, lesson_id: int, author_id: int, body: str) -> LessonQuestion:
    q = LessonQuestion(course_id=course_id, lesson_id=lesson_id, author_id=author_id, body=body.strip())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def add_lesson_answer(db: Session, *, question: LessonQuestion, author_id: int, body: str) -> LessonAnswer:
    a = LessonAnswer(question_id=question.id, author_id=author_id, body=body.strip())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def hide_lesson_question(db: Session, q: LessonQuestion) -> None:
    q.is_active = False
    db.commit()


def answered_by_staff(db: Session, q: LessonQuestion) -> bool:
    staff_roles = (Role.ADMIN, Role.STAFF, Role.INSTRUCTOR)
    return any(a.author is not None and a.author.role in staff_roles for a in q.answers)


def count_unanswered(db: Session, course_id: int) -> int:
    return sum(1 for q in list_course_questions(db, [course_id]) if not answered_by_staff(db, q))


def course_ids_with_titles(db: Session, ids: list[int]) -> list[Course]:
    if not ids:
        return []
    return list(db.scalars(select(Course).where(Course.id.in_(ids), Course.is_active.is_(True))).all())
