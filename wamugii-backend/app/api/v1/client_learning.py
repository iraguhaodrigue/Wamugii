"""
Student side of the final exam and lesson Q&A (CLIENT, active enrollment).

The exam endpoints never return correct answers. Every request re-checks the
deadline, so an attempt left open past its time is submitted with the answers
saved so far.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import DbDep, require_roles
from app.api.v1.client import _active_enrollment_or_block, _course_or_404
from app.api.v1.exams import question_read
from app.crud import course as course_crud
from app.crud import exam as exam_crud
from app.models.course import ExamAttempt, ExamAttemptStatus
from app.models.user import Role, User
from app.schemas.exam import (
    ExamAnswersSave,
    ExamEvent,
    ExamEventResult,
    ExamOverview,
    ExamResult,
    ExamSession,
    LessonAnswerCreate,
    LessonQuestionCreate,
    LessonQuestionRead,
)
from app.services import exam as exam_service
from app.services import notifications

router = APIRouter(prefix="/client", tags=["client learning"])
logger = logging.getLogger(__name__)

ClientOnly = Annotated[User, Depends(require_roles(Role.CLIENT))]


# --- final exam -----------------------------------------------------------------------------


@router.get("/courses/{course_id}/exam", response_model=ExamOverview,
            summary="Final-exam rules, eligibility and my attempts")
def exam_overview(course_id: int, db: DbDep, me: ClientOnly):
    course = _course_or_404(db, course_id)
    enrollment = _active_enrollment_or_block(db, course_id, me.id)
    return exam_service.overview(db, course, enrollment)


@router.post("/courses/{course_id}/exam/start", response_model=ExamSession,
             summary="Start the final exam (or continue the attempt in progress)")
def start_exam(course_id: int, db: DbDep, me: ClientOnly):
    course = _course_or_404(db, course_id)
    enrollment = _active_enrollment_or_block(db, course_id, me.id)
    ov = exam_service.overview(db, course, enrollment)
    if ov.in_progress_attempt_id is not None:
        attempt = exam_crud.get_attempt(db, ov.in_progress_attempt_id)
        return exam_service.session_view(db, attempt, course)
    if not ov.eligible:
        raise HTTPException(status_code=403, detail=ov.reason or "You cannot start the exam now.")
    attempt = exam_service.start_attempt(db, course, enrollment)
    logger.info("exam attempt %s started (course %s, client %s)", attempt.id, course_id, me.id)
    return exam_service.session_view(db, attempt, course)


def _own_attempt(db, attempt_id: int, me: User) -> tuple[ExamAttempt, object, object]:
    attempt = exam_crud.get_attempt(db, attempt_id)
    if attempt is None or attempt.client_id != me.id:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    course = _course_or_404(db, attempt.course_id)
    enrollment = _active_enrollment_or_block(db, attempt.course_id, me.id)
    exam_service.expire_if_due(db, attempt, course)
    return attempt, course, enrollment


@router.get("/exam-attempts/{attempt_id}", response_model=ExamSession,
            summary="Reload an exam in progress (after a refresh)")
def get_exam_session(attempt_id: int, db: DbDep, me: ClientOnly):
    attempt, course, _ = _own_attempt(db, attempt_id, me)
    if attempt.status != ExamAttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="This exam attempt has already been submitted.")
    return exam_service.session_view(db, attempt, course)


@router.put("/exam-attempts/{attempt_id}/answers",
            summary="Save answers as the student goes")
def save_exam_answers(attempt_id: int, data: ExamAnswersSave, db: DbDep, me: ClientOnly):
    attempt, _, _ = _own_attempt(db, attempt_id, me)
    if attempt.status != ExamAttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="This exam attempt has already been submitted.")
    saved = exam_service.save_answers(db, attempt, data.answers)
    return {"saved": saved}


@router.post("/exam-attempts/{attempt_id}/events", response_model=ExamEventResult,
             summary="Report leaving the exam screen; the last allowed leave submits the exam")
def report_exam_event(attempt_id: int, data: ExamEvent, db: DbDep, me: ClientOnly):
    attempt, course, enrollment = _own_attempt(db, attempt_id, me)
    if attempt.status != ExamAttemptStatus.IN_PROGRESS:
        return ExamEventResult(
            leave_count=attempt.leave_count,
            max_leaves=course.exam_max_leaves,
            submitted=True,
            result=exam_service.result_view(db, attempt, course, enrollment),
        )
    attempt = exam_service.record_event(db, attempt, course, data.type, data.detail)
    submitted = attempt.status == ExamAttemptStatus.SUBMITTED
    if data.type == "leave":
        logger.info("exam attempt %s: leave %s/%s (%s)", attempt.id, attempt.leave_count, course.exam_max_leaves, data.detail)
    return ExamEventResult(
        leave_count=attempt.leave_count,
        max_leaves=course.exam_max_leaves,
        submitted=submitted,
        result=exam_service.result_view(db, attempt, course, enrollment) if submitted else None,
    )


@router.post("/exam-attempts/{attempt_id}/submit", response_model=ExamResult,
             summary="Submit the exam for marking")
def submit_exam(attempt_id: int, db: DbDep, me: ClientOnly, data: ExamAnswersSave | None = None):
    attempt, course, enrollment = _own_attempt(db, attempt_id, me)
    if attempt.status == ExamAttemptStatus.IN_PROGRESS:
        if data is not None and data.answers:
            exam_service.save_answers(db, attempt, data.answers)
        attempt = exam_service.finish_attempt(db, attempt, course, "STUDENT")
    return exam_service.result_view(db, attempt, course, enrollment)


@router.get("/exam-attempts/{attempt_id}/result", response_model=ExamResult,
            summary="The result of a submitted attempt")
def exam_result(attempt_id: int, db: DbDep, me: ClientOnly):
    attempt, course, enrollment = _own_attempt(db, attempt_id, me)
    if attempt.status != ExamAttemptStatus.SUBMITTED:
        raise HTTPException(status_code=409, detail="This exam is still in progress.")
    return exam_service.result_view(db, attempt, course, enrollment)


# --- lesson Q&A ---------------------------------------------------------------------------------


def _lesson_or_404(db, course_id: int, lesson_id: int):
    lesson = course_crud.get_lesson_for_course(db, course_id, lesson_id)
    if lesson is None or not lesson.is_active:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get("/courses/{course_id}/lessons/{lesson_id}/questions", response_model=list[LessonQuestionRead],
            summary="Questions and answers under a lesson")
def lesson_questions(course_id: int, lesson_id: int, db: DbDep, me: ClientOnly):
    _course_or_404(db, course_id)
    _active_enrollment_or_block(db, course_id, me.id)
    _lesson_or_404(db, course_id, lesson_id)
    return [question_read(db, q, viewer=me, full_names=False) for q in exam_crud.list_lesson_questions(db, lesson_id)]


@router.post("/courses/{course_id}/lessons/{lesson_id}/questions", response_model=LessonQuestionRead, status_code=201,
             summary="Ask a question under a lesson; the course instructors are notified")
def ask_question(course_id: int, lesson_id: int, data: LessonQuestionCreate, db: DbDep, me: ClientOnly):
    course = _course_or_404(db, course_id)
    _active_enrollment_or_block(db, course_id, me.id)
    lesson = _lesson_or_404(db, course_id, lesson_id)
    q = exam_crud.create_lesson_question(db, course_id=course_id, lesson_id=lesson.id, author_id=me.id, body=data.body)
    notifications.notify_lesson_question(db, course, lesson, q, me)
    return question_read(db, q, viewer=me, full_names=False)


@router.post("/courses/{course_id}/questions/{question_id}/answers", response_model=LessonQuestionRead, status_code=201,
             summary="Reply in a lesson question thread (students can help each other)")
def reply_to_question(course_id: int, question_id: int, data: LessonAnswerCreate, db: DbDep, me: ClientOnly):
    course = _course_or_404(db, course_id)
    _active_enrollment_or_block(db, course_id, me.id)
    q = exam_crud.get_lesson_question(db, question_id)
    if q is None or q.course_id != course_id:
        raise HTTPException(status_code=404, detail="Question not found")
    exam_crud.add_lesson_answer(db, question=q, author_id=me.id, body=data.body)
    db.refresh(q)
    notifications.notify_lesson_answer(db, course, q.lesson, q, me)
    return question_read(db, q, viewer=me, full_names=False)
