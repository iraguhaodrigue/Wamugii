"""
Final exam engine: drawing questions, marking answers and finishing attempts.

How an attempt works
--------------------
1. ``start_attempt`` draws ``course.exam_question_count`` active questions,
   mixed by type in roughly the proportions of a Huawei online exam (1/6
   true/false, 1/2 single answer, 1/5 multiple answer, the rest fill in the
   blank), shuffles the options of each choice question, and stores the
   selection on the attempt. Questions are grouped by type (true/false first),
   in a random order inside each group.
2. The student's answers are saved as they go (``save_answers``).
3. The attempt ends when the student submits, when time runs out (checked on
   every request, with a short grace period for slow connections), or when the
   student leaves the exam screen ``course.exam_max_leaves`` times
   (``record_event``). All three go through ``finish_attempt``.

Marking happens only here, on the server: the correct answers never leave it.
A multiple-answer question scores only when exactly the right set of options is
chosen; a fill-in-the-blank answer is compared case-insensitively, ignoring
extra spaces and surrounding punctuation, and numbers match by value.
"""

from __future__ import annotations

import random
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.crud import course as course_crud
from app.crud import exam as exam_crud
from app.models.course import (
    Course,
    Enrollment,
    ExamAttempt,
    ExamAttemptStatus,
    ExamQuestion,
    ExamQuestionKind,
)
from app.schemas.exam import (
    ExamAttemptSummary,
    ExamOption,
    ExamOverview,
    ExamQuestionPublic,
    ExamResult,
    ExamSession,
    TopicScore,
)

# Answers arriving this long after the deadline still count (slow networks).
GRACE = timedelta(seconds=60)
MAX_EVENTS = 300

# Order of the sections in the exam, and each type's share of the questions.
KIND_ORDER = [
    ExamQuestionKind.TRUE_FALSE,
    ExamQuestionKind.SINGLE,
    ExamQuestionKind.MULTIPLE,
    ExamQuestionKind.FILL_BLANK,
]
KIND_SHARE = {
    ExamQuestionKind.TRUE_FALSE: 1 / 6,
    ExamQuestionKind.SINGLE: 1 / 2,
    ExamQuestionKind.MULTIPLE: 1 / 5,
}

_rng = random.SystemRandom()


def now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    """SQLite hands back naive datetimes; treat them as UTC."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# --- drawing ---------------------------------------------------------------------


def plan_counts(total: int, pools: dict[ExamQuestionKind, int]) -> dict[ExamQuestionKind, int]:
    """How many of each type to draw, topping up from other types when one is short."""
    want = {k: round(total * share) for k, share in KIND_SHARE.items()}
    want[ExamQuestionKind.FILL_BLANK] = max(0, total - sum(want.values()))
    take = {k: min(want.get(k, 0), pools.get(k, 0)) for k in KIND_ORDER}
    short = total - sum(take.values())
    # Top up from whichever types still have unused questions, singles first.
    for k in [ExamQuestionKind.SINGLE, ExamQuestionKind.MULTIPLE, ExamQuestionKind.TRUE_FALSE, ExamQuestionKind.FILL_BLANK]:
        if short <= 0:
            break
        extra = min(short, pools.get(k, 0) - take[k])
        take[k] += extra
        short -= extra
    return take


def draw_questions(questions: list[ExamQuestion], total: int) -> tuple[list[int], dict[str, list[int]]]:
    pools: dict[ExamQuestionKind, list[ExamQuestion]] = {k: [] for k in KIND_ORDER}
    for q in questions:
        pools[q.kind].append(q)
    counts = plan_counts(total, {k: len(v) for k, v in pools.items()})
    chosen: list[int] = []
    orders: dict[str, list[int]] = {}
    for kind in KIND_ORDER:
        picked = _rng.sample(pools[kind], counts[kind])
        for q in picked:
            chosen.append(q.id)
            if kind in (ExamQuestionKind.SINGLE, ExamQuestionKind.MULTIPLE):
                order = list(range(len(q.options)))
                _rng.shuffle(order)
                orders[str(q.id)] = order
            elif kind == ExamQuestionKind.TRUE_FALSE:
                orders[str(q.id)] = [0, 1]
    return chosen, orders


# --- marking ---------------------------------------------------------------------


def _norm(text: str) -> str:
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,;:!?\"'`()[]")


def _as_number(text: str) -> float | None:
    try:
        return float(str(text).strip().replace(",", "").replace(" ", "").rstrip("%"))
    except ValueError:
        return None


def is_correct(q: ExamQuestion, answer) -> bool:
    if answer is None:
        return False
    if q.kind in (ExamQuestionKind.SINGLE, ExamQuestionKind.TRUE_FALSE):
        try:
            return int(answer) == int(q.correct[0])
        except (TypeError, ValueError, IndexError):
            return False
    if q.kind == ExamQuestionKind.MULTIPLE:
        if not isinstance(answer, list):
            return False
        try:
            return sorted({int(a) for a in answer}) == sorted(int(c) for c in q.correct)
        except (TypeError, ValueError):
            return False
    # FILL_BLANK: numbers match by value ("0.96" = ".96" = "0.960"), text
    # case-insensitively without surrounding spaces or punctuation.
    given = _norm(str(answer))
    if not given:
        return False
    given_num = _as_number(str(answer))
    for accepted in q.correct:
        acc_num = _as_number(str(accepted))
        if given_num is not None and acc_num is not None:
            if abs(given_num - acc_num) < 1e-9:
                return True
            continue
        if given == _norm(str(accepted)):
            return True
    return False


def _clean_answer(q: ExamQuestion, value):
    """Keep only answers of the right shape; anything else is treated as blank."""
    if value is None:
        return None
    if q.kind in (ExamQuestionKind.SINGLE, ExamQuestionKind.TRUE_FALSE):
        if isinstance(value, bool) or not isinstance(value, int):
            return None
        return value if 0 <= value < len(q.options) else None
    if q.kind == ExamQuestionKind.MULTIPLE:
        if not isinstance(value, list):
            return None
        vals = sorted({v for v in value if isinstance(v, int) and not isinstance(v, bool) and 0 <= v < len(q.options)})
        return vals or None
    text = str(value)[:300]
    return text if text.strip() else None


# --- attempt lifecycle ----------------------------------------------------------


def attempts_allowed(course: Course, enrollment: Enrollment) -> int:
    return course.exam_max_attempts + (enrollment.exam_extra_attempts or 0)


def finish_attempt(db: Session, attempt: ExamAttempt, course: Course, reason: str) -> ExamAttempt:
    """Mark and close an attempt. Safe to call twice: a finished attempt is returned as is."""
    if attempt.status == ExamAttemptStatus.SUBMITTED:
        return attempt
    by_id = {q.id: q for q in exam_crud.list_exam_questions(db, course.id)}
    answers = attempt.answers or {}
    score = 0
    topics: dict[str, list[int]] = {}
    for qid in attempt.question_ids:
        q = by_id.get(qid)
        if q is None:
            continue
        ok = is_correct(q, answers.get(str(qid)))
        score += int(ok)
        bucket = topics.setdefault(q.topic or "General", [0, 0])
        bucket[0] += int(ok)
        bucket[1] += 1
    total = len(attempt.question_ids)
    percent = int(round(100 * score / total)) if total else 0
    attempt.score = score
    attempt.total = total
    attempt.percent = percent
    attempt.passed = total > 0 and percent >= course.exam_pass_percent
    attempt.topic_scores = [{"topic": t, "correct": c, "total": n} for t, (c, n) in topics.items()]
    attempt.status = ExamAttemptStatus.SUBMITTED
    attempt.submitted_at = now()
    attempt.submit_reason = reason
    db.commit()
    db.refresh(attempt)
    if attempt.passed:
        _celebrate_pass(db, attempt, course)
    return attempt


def _celebrate_pass(db: Session, attempt: ExamAttempt, course: Course) -> None:
    """First pass only: in-app notification + certificate email (best effort)."""
    from app.services import notifications

    earlier = [
        a for a in exam_crud.list_attempts_for_enrollment(db, attempt.enrollment_id)
        if a.passed and a.id != attempt.id
    ]
    if earlier:
        return
    enrollment = course_crud.get_enrollment(db, attempt.enrollment_id)
    if enrollment is not None:
        notifications.notify_exam_passed(db, enrollment, course, attempt)


def expire_if_due(db: Session, attempt: ExamAttempt, course: Course) -> ExamAttempt:
    if attempt.status == ExamAttemptStatus.IN_PROGRESS and now() > _aware(attempt.deadline_at) + GRACE:
        return finish_attempt(db, attempt, course, "TIME_UP")
    return attempt


def start_attempt(db: Session, course: Course, enrollment: Enrollment) -> ExamAttempt:
    questions = exam_crud.list_exam_questions(db, course.id, active_only=True)
    total = min(course.exam_question_count, len(questions))
    ids, orders = draw_questions(questions, total)
    started = now()
    attempt = ExamAttempt(
        course_id=course.id,
        enrollment_id=enrollment.id,
        client_id=enrollment.client_id,
        status=ExamAttemptStatus.IN_PROGRESS,
        started_at=started,
        deadline_at=started + timedelta(minutes=course.exam_minutes),
        question_ids=ids,
        option_orders=orders,
        answers={},
        leave_count=0,
        events=[{"type": "start", "at": started.isoformat()}],
        total=len(ids),
        passed=False,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def save_answers(db: Session, attempt: ExamAttempt, incoming: dict) -> int:
    by_id = {q.id: q for q in exam_crud.list_exam_questions(db, attempt.course_id)}
    allowed = set(attempt.question_ids)
    answers = dict(attempt.answers or {})
    saved = 0
    for key, value in incoming.items():
        try:
            qid = int(key)
        except (TypeError, ValueError):
            continue
        if qid not in allowed or qid not in by_id:
            continue
        cleaned = _clean_answer(by_id[qid], value)
        if cleaned is None:
            answers.pop(str(qid), None)
        else:
            answers[str(qid)] = cleaned
        saved += 1
    attempt.answers = answers  # reassign so the JSON column is marked dirty
    db.commit()
    return saved


def record_event(db: Session, attempt: ExamAttempt, course: Course, event_type: str, detail: str) -> ExamAttempt:
    events = list(attempt.events or [])
    if len(events) < MAX_EVENTS:
        events.append({"type": event_type, "detail": detail, "at": now().isoformat()})
    attempt.events = events
    if event_type == "leave":
        attempt.leave_count = (attempt.leave_count or 0) + 1
    db.commit()
    db.refresh(attempt)
    if event_type == "leave" and attempt.leave_count >= course.exam_max_leaves:
        return finish_attempt(db, attempt, course, "LEAVE_LIMIT")
    return attempt


# --- views ----------------------------------------------------------------------------


def session_view(db: Session, attempt: ExamAttempt, course: Course) -> ExamSession:
    by_id = {q.id: q for q in exam_crud.list_exam_questions(db, course.id)}
    out: list[ExamQuestionPublic] = []
    for n, qid in enumerate(attempt.question_ids, start=1):
        q = by_id.get(qid)
        if q is None:
            continue
        order = (attempt.option_orders or {}).get(str(qid), list(range(len(q.options))))
        options = [ExamOption(id=i, text=q.options[i]) for i in order if 0 <= i < len(q.options)]
        out.append(ExamQuestionPublic(id=q.id, number=n, kind=q.kind, question=q.question, options=options))
    return ExamSession(
        attempt_id=attempt.id,
        course_id=course.id,
        course_title=course.title,
        started_at=_aware(attempt.started_at),
        deadline_at=_aware(attempt.deadline_at),
        server_now=now(),
        leave_count=attempt.leave_count,
        max_leaves=course.exam_max_leaves,
        pass_percent=course.exam_pass_percent,
        questions=out,
        answers=attempt.answers or {},
    )


def _next_attempt_at(course: Course, attempts: list[ExamAttempt]) -> datetime | None:
    finished = [a for a in attempts if a.status == ExamAttemptStatus.SUBMITTED]
    if not finished or course.exam_cooldown_hours <= 0:
        return None
    last = max(_aware(a.submitted_at) or _aware(a.started_at) for a in finished)
    when = last + timedelta(hours=course.exam_cooldown_hours)
    return when if when > now() else None


def overview(db: Session, course: Course, enrollment: Enrollment) -> ExamOverview:
    bank = exam_crud.list_exam_questions(db, course.id, active_only=True)
    attempts = exam_crud.list_attempts_for_enrollment(db, enrollment.id)
    for a in attempts:
        expire_if_due(db, a, course)
    total_lessons = course_crud.count_active_lessons(db, course.id)
    completed = course_crud.count_completed_lessons(db, enrollment.id)
    lessons_complete = course_crud.progress_percent(completed, total_lessons) >= 100
    finished = [a for a in attempts if a.status == ExamAttemptStatus.SUBMITTED]
    in_progress = next((a for a in attempts if a.status == ExamAttemptStatus.IN_PROGRESS), None)
    passed = any(a.passed for a in finished)
    best = max((a.percent for a in finished if a.percent is not None), default=None)
    allowed = attempts_allowed(course, enrollment)
    used = len(finished) + (1 if in_progress else 0)
    left = max(0, allowed - used)
    next_at = None if passed else _next_attempt_at(course, attempts)

    counts = plan_counts(min(course.exam_question_count, len(bank)), {
        k: sum(1 for q in bank if q.kind == k) for k in KIND_ORDER
    })

    eligible, reason = True, ""
    if not bank:
        eligible, reason = False, "This course does not have a final exam yet."
    elif passed:
        eligible, reason = False, "You have passed the final exam."
    elif in_progress:
        eligible, reason = True, "You have an exam in progress. Continue it before the time runs out."
    elif not lessons_complete:
        eligible, reason = False, "Complete every lesson to unlock the final exam."
    elif left <= 0:
        eligible, reason = False, "You have used all your attempts. Contact your instructor for another attempt."
    elif next_at is not None:
        eligible, reason = False, "Take a break and review the lessons before your next attempt."

    return ExamOverview(
        available=bool(bank),
        eligible=eligible,
        reason=reason,
        lessons_complete=lessons_complete,
        question_count=min(course.exam_question_count, len(bank)),
        minutes=course.exam_minutes,
        pass_percent=course.exam_pass_percent,
        max_attempts=allowed,
        attempts_used=used,
        attempts_left=left,
        next_attempt_at=next_at,
        max_leaves=course.exam_max_leaves,
        passed=passed,
        best_percent=best,
        in_progress_attempt_id=in_progress.id if in_progress else None,
        type_counts={k.value: v for k, v in counts.items()},
        attempts=[ExamAttemptSummary.model_validate(a) for a in reversed(attempts)],
    )


def result_view(db: Session, attempt: ExamAttempt, course: Course, enrollment: Enrollment) -> ExamResult:
    attempts = exam_crud.list_attempts_for_enrollment(db, enrollment.id)
    finished = [a for a in attempts if a.status == ExamAttemptStatus.SUBMITTED]
    allowed = attempts_allowed(course, enrollment)
    passed_any = any(a.passed for a in finished)
    total_lessons = course_crud.count_active_lessons(db, course.id)
    completed = course_crud.count_completed_lessons(db, enrollment.id)
    return ExamResult(
        attempt_id=attempt.id,
        score=attempt.score or 0,
        total=attempt.total,
        percent=attempt.percent or 0,
        pass_percent=course.exam_pass_percent,
        passed=attempt.passed,
        submit_reason=attempt.submit_reason or "STUDENT",
        topic_scores=[TopicScore(**t) for t in (attempt.topic_scores or [])],
        attempts_left=0 if passed_any else max(0, allowed - len(finished)),
        next_attempt_at=None if passed_any else _next_attempt_at(course, attempts),
        certificate_ready=passed_any and course_crud.progress_percent(completed, total_lessons) >= 100,
    )


def has_exam(db: Session, course_id: int) -> bool:
    return exam_crud.count_active_exam_questions(db, course_id) > 0
