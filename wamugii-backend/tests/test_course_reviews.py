"""
Course star ratings and reviews, and the Student Handbook on course pages.

The rules that matter: only students who have really studied (active
enrollment, at least a quarter of the lessons done) can rate; one review per
student; hidden reviews leave the average; the public never sees surnames or
emails; the free sample chapter only exists for courses with a handbook.
"""

import json
from urllib.parse import unquote

import pytest

from app.services import course_reviews
from tests.test_courses import _add_lesson, _auth, _create_course, _make_client


@pytest.fixture(autouse=True)
def _quiet_email(monkeypatch):
    from app.services import email_service

    monkeypatch.setattr(email_service, "send_email", lambda *a, **k: True)


def _course_with_lessons(client, admin_headers, n=8, **overrides):
    course = _create_course(client, admin_headers, **overrides)
    lessons = [
        _add_lesson(client, admin_headers, course["id"], title=f"Lesson {i}", display_order=i)
        for i in range(1, n + 1)
    ]
    return course, lessons


def _student(client, course, email, name="Aline Uwase Mukamana", done=0, lessons=()):
    user = _make_client(email, name)
    headers = _auth(user)
    assert client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=headers).status_code == 200
    for lesson in list(lessons)[:done]:
        r = client.post(f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/complete", headers=headers)
        assert r.status_code == 200, r.text
    return headers


def test_short_name_keeps_first_name_and_initial():
    assert course_reviews.short_name("Aline Uwase Mukamana") == "Aline M."
    assert course_reviews.short_name("Jean") == "Jean"
    assert course_reviews.short_name("  ") == "Student"


def test_student_must_study_a_quarter_of_the_course_before_rating(client, admin_headers):
    course, lessons = _course_with_lessons(client, admin_headers, n=8)
    headers = _student(client, course, "early@example.com", done=1, lessons=lessons)

    status = client.get(f"/api/v1/client/courses/{course['id']}/review", headers=headers).json()
    assert status["can_review"] is False
    assert status["lessons_needed"] == 2  # a quarter of 8
    assert status["completed_lessons"] == 1
    assert "Complete 2 lessons" in status["reason"]

    r = client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": 5}, headers=headers)
    assert r.status_code == 403


def test_a_student_who_is_not_enrolled_cannot_rate(client, admin_headers, client_headers):
    course, _ = _course_with_lessons(client, admin_headers, n=4)
    status = client.get(f"/api/v1/client/courses/{course['id']}/review", headers=client_headers).json()
    assert status["can_review"] is False
    r = client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": 4}, headers=client_headers)
    assert r.status_code == 403


def test_rating_creates_then_updates_one_review(client, admin_headers):
    course, lessons = _course_with_lessons(client, admin_headers, n=4)
    headers = _student(client, course, "rater@example.com", done=1, lessons=lessons)

    r = client.put(
        f"/api/v1/client/courses/{course['id']}/review",
        json={"rating": 4, "comment": "  Clear lessons, good examples.  "},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["can_review"] is True
    assert body["review"]["rating"] == 4
    assert body["review"]["comment"] == "Clear lessons, good examples."
    assert body["review"]["reviewer_name"] == "Aline M."

    r = client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": 5, "comment": ""}, headers=headers)
    assert r.json()["review"]["rating"] == 5
    assert r.json()["review"]["comment"] is None

    page = client.get(f"/api/v1/courses/{course['slug']}/reviews").json()
    assert page["summary"]["count"] == 1
    assert page["summary"]["average"] == 5.0
    assert page["summary"]["distribution"]["5"] == 1
    # A rating without a comment counts in the average but is not listed.
    assert page["reviews"] == []


@pytest.mark.parametrize("rating", [0, 6])
def test_rating_must_be_one_to_five(client, admin_headers, rating):
    course, lessons = _course_with_lessons(client, admin_headers, n=4)
    headers = _student(client, course, f"bad{rating}@example.com", done=1, lessons=lessons)
    r = client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": rating}, headers=headers)
    assert r.status_code == 422


def test_comment_length_is_limited(client, admin_headers):
    course, lessons = _course_with_lessons(client, admin_headers, n=4)
    headers = _student(client, course, "long@example.com", done=1, lessons=lessons)
    r = client.put(
        f"/api/v1/client/courses/{course['id']}/review", json={"rating": 3, "comment": "x" * 1001}, headers=headers
    )
    assert r.status_code == 422


def test_public_reviews_show_average_and_hide_private_details(client, admin_headers):
    course, lessons = _course_with_lessons(client, admin_headers, n=4)
    for i, (rating, name) in enumerate([(5, "Aline Uwase"), (4, "Jean Bosco Habimana"), (3, "Grace")]):
        headers = _student(client, course, f"s{i}@example.com", name=name, done=1, lessons=lessons)
        client.put(
            f"/api/v1/client/courses/{course['id']}/review",
            json={"rating": rating, "comment": f"Comment {i}"},
            headers=headers,
        )
    page = client.get(f"/api/v1/courses/{course['slug']}/reviews").json()
    assert page["summary"]["count"] == 3
    assert page["summary"]["average"] == 4.0
    assert page["total_with_comments"] == 3
    names = {r["reviewer_name"] for r in page["reviews"]}
    assert names == {"Aline U.", "Jean H.", "Grace"}
    text = json.dumps(page)
    assert "@example.com" not in text and "Habimana" not in text

    detail = client.get(f"/api/v1/courses/{course['slug']}").json()
    assert detail["rating_average"] == 4.0 and detail["rating_count"] == 3
    listing = client.get("/api/v1/courses").json()
    card = next(c for c in listing if c["id"] == course["id"])
    assert card["rating_average"] == 4.0 and card["rating_count"] == 3


def test_staff_can_hide_a_review_and_it_leaves_the_average(client, admin_headers, staff_headers, client_headers):
    course, lessons = _course_with_lessons(client, admin_headers, n=4)
    good = _student(client, course, "good@example.com", done=1, lessons=lessons)
    bad = _student(client, course, "spam@example.com", name="Spam Bot", done=1, lessons=lessons)
    client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": 5, "comment": "Great"}, headers=good)
    client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": 1, "comment": "buy now"}, headers=bad)

    # Clients cannot moderate.
    assert client.get(f"/api/v1/courses/by-id/{course['id']}/reviews", headers=client_headers).status_code == 403

    rows = client.get(f"/api/v1/courses/by-id/{course['id']}/reviews", headers=staff_headers).json()
    spam = next(r for r in rows if r["reviewer_full_name"] == "Spam Bot")
    r = client.patch(
        f"/api/v1/courses/by-id/{course['id']}/reviews/{spam['id']}", json={"is_hidden": True}, headers=staff_headers
    )
    assert r.status_code == 200 and r.json()["is_hidden"] is True

    page = client.get(f"/api/v1/courses/{course['slug']}/reviews").json()
    assert page["summary"]["count"] == 1 and page["summary"]["average"] == 5.0
    assert [x["comment"] for x in page["reviews"]] == ["Great"]

    # A review id from another course is a 404.
    other, _ = _course_with_lessons(client, admin_headers, n=1, title="Other course")
    r = client.patch(
        f"/api/v1/courses/by-id/{other['id']}/reviews/{spam['id']}", json={"is_hidden": False}, headers=staff_headers
    )
    assert r.status_code == 404


def test_student_can_delete_their_review(client, admin_headers):
    course, lessons = _course_with_lessons(client, admin_headers, n=4)
    headers = _student(client, course, "del@example.com", done=1, lessons=lessons)
    client.put(f"/api/v1/client/courses/{course['id']}/review", json={"rating": 2}, headers=headers)
    assert client.delete(f"/api/v1/client/courses/{course['id']}/review", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/client/courses/{course['id']}/review", headers=headers).status_code == 404
    assert client.get(f"/api/v1/courses/{course['slug']}/reviews").json()["summary"]["count"] == 0


def test_reviews_of_a_draft_course_are_hidden(client, admin_headers):
    course = _create_course(client, admin_headers, status="DRAFT")
    assert client.get(f"/api/v1/courses/{course['slug']}/reviews").status_code == 404


def test_detail_lists_instructors(client, admin_headers):
    from app.crud import user as user_crud
    from app.models.user import Role
    from app.schemas.user import UserCreate
    from tests.conftest import TestingSessionLocal

    course, _ = _course_with_lessons(client, admin_headers, n=1)
    db = TestingSessionLocal()
    try:
        teacher = user_crud.create(
            db, UserCreate(full_name="Jean Teacher", email="teacher@example.com", password="password123"), role=Role.INSTRUCTOR
        )
        assert teacher.id
    finally:
        db.close()
    r = client.post(f"/api/v1/courses/{course['id']}/instructors", json={"email": "teacher@example.com"}, headers=admin_headers)
    assert r.status_code in (200, 201), r.text
    detail = client.get(f"/api/v1/courses/{course['slug']}").json()
    assert detail["instructors"] == ["Jean Teacher"]


def test_handbook_and_sample_chapter(client, admin_headers, tmp_path, monkeypatch):
    course, _ = _course_with_lessons(client, admin_headers, n=1, title="Handbook Course")
    slug = course["slug"]
    monkeypatch.setattr(course_reviews, "CONTENT_ROOT", tmp_path)

    # No handbook built: no handbook info and no sample.
    assert client.get(f"/api/v1/courses/{slug}").json()["handbook"] is None
    assert client.get(f"/api/v1/courses/{slug}/sample-chapter").status_code == 404

    (tmp_path / "handbooks" / slug).mkdir(parents=True)
    (tmp_path / "handbooks" / slug / "handbook.json").write_text(json.dumps({"pages": 197, "words": 65000, "chapters": 24}))
    (tmp_path / "pdfs" / slug).mkdir(parents=True)
    (tmp_path / "pdfs" / slug / "01.pdf").write_bytes(b"%PDF-1.7 sample")

    info = client.get(f"/api/v1/courses/{slug}").json()["handbook"]
    assert info == {"pages": 197, "words": 65000, "chapters": 24, "sample_available": True}
    r = client.get(f"/api/v1/courses/{slug}/sample-chapter")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "Sample chapter" in unquote(r.headers["content-disposition"])
    assert r.content.startswith(b"%PDF")
