"""
Final exams, instructors and lesson Q&A.

The exam rules under test: answers never leave the server, the certificate
waits for a pass, leaving the screen max_leaves times submits the attempt,
the deadline submits it too, attempts are limited and spaced, and an
instructor reaches only the courses they are assigned to.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.course import ExamAttempt
from tests.conftest import TestingSessionLocal
from tests.test_courses import _add_lesson, _auth, _create_course, _make_client, sent_emails  # noqa: F401


def _bank():
    qs = []
    for i in range(12):
        qs.append({"kind": "TRUE_FALSE", "question": f"Statement {i} is true.", "options": [], "correct": [0], "topic": "Week 1"})
    for i in range(30):
        qs.append({"kind": "SINGLE", "question": f"Single {i}?", "options": ["right", "wrong a", "wrong b", "wrong c"], "correct": [0], "topic": "Week 2"})
    for i in range(14):
        qs.append({"kind": "MULTIPLE", "question": f"Multiple {i}?", "options": ["yes 1", "yes 2", "no 1", "no 2"], "correct": [0, 1], "topic": "Week 3"})
    for i in range(10):
        qs.append({"kind": "FILL_BLANK", "question": f"Python counts from ___ (item {i}).", "options": [], "correct": ["0", "zero"], "topic": "Week 4"})
    return qs


@pytest.fixture
def exam_course(client, admin_headers):
    course = _create_course(client, admin_headers, title="Exam Course")
    lesson = _add_lesson(client, admin_headers, course["id"], title="Only lesson")
    resp = client.post(f"/api/v1/courses/{course['id']}/exam/questions", json=_bank(), headers=admin_headers)
    assert resp.status_code == 201, resp.text
    resp = client.put(
        f"/api/v1/courses/{course['id']}/exam/settings",
        json={"exam_question_count": 20, "exam_minutes": 30, "exam_cooldown_hours": 0},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    return course, lesson


def _student(client, course, lesson, email="exam@example.com", complete=True):
    user = _make_client(email)
    h = _auth(user)
    assert client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=h).status_code in (200, 201)
    if complete:
        r = client.post(f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/complete", headers=h)
        assert r.status_code == 200, r.text
    return user, h


def _correct_answers(session):
    """Answer every question correctly using the known bank shapes."""
    out = {}
    for q in session["questions"]:
        if q["kind"] == "TRUE_FALSE":
            out[str(q["id"])] = 0
        elif q["kind"] == "SINGLE":
            out[str(q["id"])] = next(o["id"] for o in q["options"] if o["text"] == "right")
        elif q["kind"] == "MULTIPLE":
            out[str(q["id"])] = [o["id"] for o in q["options"] if o["text"].startswith("yes")]
        else:
            out[str(q["id"])] = "  Zero. "
    return out


def test_bad_exam_questions_are_rejected(client, admin_headers):
    course = _create_course(client, admin_headers)
    url = f"/api/v1/courses/{course['id']}/exam/questions"
    bad = [
        {"kind": "SINGLE", "question": "Pick one", "options": ["a", "b"], "correct": [0, 1]},
        {"kind": "MULTIPLE", "question": "Pick some", "options": ["a", "b", "c"], "correct": [0]},
        {"kind": "FILL_BLANK", "question": "No blank here", "options": [], "correct": ["x"]},
        {"kind": "SINGLE", "question": "Out of range", "options": ["a", "b"], "correct": [5]},
    ]
    for item in bad:
        assert client.post(url, json=[item], headers=admin_headers).status_code == 422


def test_exam_locked_until_lessons_done_and_answers_stay_secret(client, admin_headers, exam_course):
    course, lesson = exam_course
    _, h = _student(client, course, lesson, complete=False)
    ov = client.get(f"/api/v1/client/courses/{course['id']}/exam", headers=h).json()
    assert ov["available"] is True and ov["eligible"] is False
    assert "Complete every lesson" in ov["reason"]
    assert client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).status_code == 403

    client.post(f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/complete", headers=h)
    session = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
    assert len(session["questions"]) == 20
    kinds = [q["kind"] for q in session["questions"]]
    # grouped by type, true/false first, all four types present
    assert kinds == sorted(kinds, key=["TRUE_FALSE", "SINGLE", "MULTIPLE", "FILL_BLANK"].index)
    assert set(kinds) == {"TRUE_FALSE", "SINGLE", "MULTIPLE", "FILL_BLANK"}
    text = str(session)
    assert "correct" not in text and "explanation" not in text


def test_full_marks_pass_unlocks_certificate_and_emails_once(client, admin_headers, exam_course, sent_emails):
    course, lesson = exam_course
    _, h = _student(client, course, lesson)
    # lessons done, exam not passed yet -> no certificate, and the email says "exam unlocked"
    assert client.get(f"/api/v1/client/courses/{course['id']}/certificate", headers=h).status_code == 403
    assert any("final exam is unlocked" in e["subject"] for e in sent_emails)

    session = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
    aid = session["attempt_id"]
    assert client.put(f"/api/v1/client/exam-attempts/{aid}/answers", json={"answers": _correct_answers(session)}, headers=h).status_code == 200
    res = client.post(f"/api/v1/client/exam-attempts/{aid}/submit", headers=h).json()
    assert res["percent"] == 100 and res["passed"] is True and res["certificate_ready"] is True
    assert {t["topic"] for t in res["topic_scores"]} == {"Week 1", "Week 2", "Week 3", "Week 4"}

    cert = client.get(f"/api/v1/client/courses/{course['id']}/certificate", headers=h).json()
    assert cert["exam_percent"] == 100
    assert sum("You passed" in e["subject"] for e in sent_emails) == 1
    ov = client.get(f"/api/v1/client/courses/{course['id']}/exam", headers=h).json()
    assert ov["passed"] is True and ov["eligible"] is False


def test_multiple_answer_needs_the_exact_set(client, admin_headers, exam_course):
    course, lesson = exam_course
    _, h = _student(client, course, lesson)
    session = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
    answers = _correct_answers(session)
    multi = [q for q in session["questions"] if q["kind"] == "MULTIPLE"]
    for q in multi:  # choose only one of the two right options
        answers[str(q["id"])] = answers[str(q["id"])][:1]
    res = client.post(f"/api/v1/client/exam-attempts/{session['attempt_id']}/submit", json={"answers": answers}, headers=h).json()
    assert res["score"] == len(session["questions"]) - len(multi)


def test_third_leave_submits_the_exam(client, admin_headers, exam_course):
    course, lesson = exam_course
    _, h = _student(client, course, lesson)
    session = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
    aid = session["attempt_id"]
    url = f"/api/v1/client/exam-attempts/{aid}/events"
    r1 = client.post(url, json={"type": "leave", "detail": "tab_hidden"}, headers=h).json()
    assert r1["leave_count"] == 1 and r1["submitted"] is False
    r_notice = client.post(url, json={"type": "notice", "detail": "copy"}, headers=h).json()
    assert r_notice["leave_count"] == 1  # notices are logged, not counted
    client.post(url, json={"type": "leave", "detail": "window_blur"}, headers=h)
    r3 = client.post(url, json={"type": "leave", "detail": "fullscreen_exit"}, headers=h).json()
    assert r3["submitted"] is True and r3["result"]["submit_reason"] == "LEAVE_LIMIT"
    # the attempt is closed for good
    assert client.put(f"/api/v1/client/exam-attempts/{aid}/answers", json={"answers": {}}, headers=h).status_code == 409


def test_time_up_submits_with_saved_answers(client, admin_headers, exam_course):
    course, lesson = exam_course
    _, h = _student(client, course, lesson)
    session = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
    aid = session["attempt_id"]
    client.put(f"/api/v1/client/exam-attempts/{aid}/answers", json={"answers": _correct_answers(session)}, headers=h)
    db = TestingSessionLocal()
    try:
        a = db.get(ExamAttempt, aid)
        a.deadline_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.commit()
    finally:
        db.close()
    res = client.get(f"/api/v1/client/exam-attempts/{aid}/result", headers=h).json()
    assert res["submit_reason"] == "TIME_UP" and res["percent"] == 100


def test_attempts_are_limited_and_instructor_can_grant_one_more(client, admin_headers, exam_course):
    course, lesson = exam_course
    user, h = _student(client, course, lesson)
    for _ in range(3):
        s = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
        r = client.post(f"/api/v1/client/exam-attempts/{s['attempt_id']}/submit", headers=h).json()
        assert r["passed"] is False
    ov = client.get(f"/api/v1/client/courses/{course['id']}/exam", headers=h).json()
    assert ov["attempts_left"] == 0 and ov["eligible"] is False
    assert client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).status_code == 403

    enrollments = client.get(f"/api/v1/courses/{course['id']}/enrollments", headers=admin_headers).json()
    mine = next(e for e in enrollments if e["client_id"] == user.id)
    assert mine["exam_attempts"] == 3 and mine["exam_passed"] is False
    r = client.post(f"/api/v1/courses/{course['id']}/enrollments/{mine['id']}/exam/extra-attempt", headers=admin_headers)
    assert r.status_code == 200
    ov = client.get(f"/api/v1/client/courses/{course['id']}/exam", headers=h).json()
    assert ov["attempts_left"] == 1 and ov["eligible"] is True


def test_cooldown_blocks_an_immediate_retry(client, admin_headers, exam_course):
    course, lesson = exam_course
    client.put(f"/api/v1/courses/{course['id']}/exam/settings", json={"exam_cooldown_hours": 24}, headers=admin_headers)
    _, h = _student(client, course, lesson)
    s = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h).json()
    client.post(f"/api/v1/client/exam-attempts/{s['attempt_id']}/submit", headers=h)
    ov = client.get(f"/api/v1/client/courses/{course['id']}/exam", headers=h).json()
    assert ov["eligible"] is False and ov["next_attempt_at"] is not None


def test_another_student_cannot_touch_my_attempt(client, admin_headers, exam_course):
    course, lesson = exam_course
    _, h1 = _student(client, course, lesson, email="one@example.com")
    _, h2 = _student(client, course, lesson, email="two@example.com")
    s = client.post(f"/api/v1/client/courses/{course['id']}/exam/start", headers=h1).json()
    assert client.get(f"/api/v1/client/exam-attempts/{s['attempt_id']}", headers=h2).status_code == 404
    assert client.post(f"/api/v1/client/exam-attempts/{s['attempt_id']}/submit", headers=h2).status_code == 404


def test_instructor_edits_only_assigned_courses(client, admin_headers, exam_course, sent_emails):
    course, lesson = exam_course
    other = _create_course(client, admin_headers, title="Other Course")
    teacher = _make_client("teacher@example.com", name="Grace Teacher")
    th = _auth(teacher)

    r = client.post(f"/api/v1/courses/{course['id']}/instructors", json={"email": "teacher@example.com"}, headers=admin_headers)
    assert r.status_code == 201, r.text
    assert any("You are now an instructor" in e["subject"] for e in sent_emails)
    # promoted to INSTRUCTOR
    assert client.get("/api/v1/users/me", headers=th).json()["role"] == "INSTRUCTOR"

    mine = client.get("/api/v1/instructor/courses", headers=th).json()
    assert [c["id"] for c in mine] == [course["id"]]
    # can edit lessons, quiz and exam on their course ...
    assert client.patch(f"/api/v1/courses/{course['id']}/lessons/{lesson['id']}", json={"title": "Renamed"}, headers=th).status_code == 200
    assert client.get(f"/api/v1/courses/{course['id']}/exam", headers=th).status_code == 200
    assert client.get(f"/api/v1/courses/{course['id']}/enrollments", headers=th).status_code == 200
    # ... but not other courses, and never price/publishing
    assert client.get(f"/api/v1/courses/{other['id']}/exam", headers=th).status_code == 403
    assert client.post(f"/api/v1/courses/{other['id']}/lessons", json={"title": "x"}, headers=th).status_code == 403
    assert client.patch(f"/api/v1/courses/{course['id']}", json={"status": "DRAFT"}, headers=th).status_code == 403
    # an instructor cannot assign instructors
    assert client.post(f"/api/v1/courses/{course['id']}/instructors", json={"email": "x@example.com"}, headers=th).status_code == 403


def test_lesson_questions_reach_the_instructor_and_answers_reach_the_student(client, admin_headers, exam_course, sent_emails):
    course, lesson = exam_course
    teacher = _make_client("teach2@example.com", name="Eric Mentor")
    client.post(f"/api/v1/courses/{course['id']}/instructors", json={"email": "teach2@example.com"}, headers=admin_headers)
    th = _auth(teacher)
    student, sh = _student(client, course, lesson, email="asker@example.com", complete=False)

    r = client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/questions",
        json={"body": "Why does Python count from zero?"},
        headers=sh,
    )
    assert r.status_code == 201, r.text
    qid = r.json()["id"]
    assert any(e["to_email"] == "teach2@example.com" and "New question" in e["subject"] for e in sent_emails)

    inbox = client.get("/api/v1/instructor/questions?unanswered=true", headers=th).json()
    assert [q["id"] for q in inbox] == [qid]

    r = client.post(f"/api/v1/courses/{course['id']}/questions/{qid}/answers", json={"body": "Offsets start at 0."}, headers=th)
    assert r.status_code == 201
    assert r.json()["answers"][0]["author_role"] == "Instructor"
    assert any(e["to_email"] == "asker@example.com" and "has an answer" in e["subject"] for e in sent_emails)
    assert client.get("/api/v1/instructor/questions?unanswered=true", headers=th).json() == []

    thread = client.get(f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/questions", headers=sh).json()
    assert thread[0]["is_mine"] is True and thread[0]["answered_by_instructor"] is True


def test_non_enrolled_client_cannot_read_or_ask(client, admin_headers, exam_course):
    course, lesson = exam_course
    outsider = _auth(_make_client("outsider@example.com"))
    url = f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/questions"
    assert client.get(url, headers=outsider).status_code == 404
    assert client.post(url, json={"body": "hello there"}, headers=outsider).status_code == 404


def test_course_without_exam_keeps_the_old_certificate_rule(client, admin_headers, sent_emails):
    course = _create_course(client, admin_headers, title="No Exam")
    lesson = _add_lesson(client, admin_headers, course["id"])
    _, h = _student(client, course, lesson, email="noexam@example.com")
    cert = client.get(f"/api/v1/client/courses/{course['id']}/certificate", headers=h)
    assert cert.status_code == 200 and cert.json()["exam_percent"] is None


def test_lesson_extra_videos_round_trip(client, admin_headers):
    course = _create_course(client, admin_headers)
    lesson = _add_lesson(
        client, admin_headers, course["id"],
        extra_videos=[{"title": "Full lecture", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "minutes": 19}],
    )
    assert lesson["extra_videos"][0]["title"] == "Full lecture"
