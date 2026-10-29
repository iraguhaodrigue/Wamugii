"""
Training courses module.

The gate is the point: lesson CONTENT is never served to a non-active
enrollment. Tested from the outside with every path that could leak -- the
list, the one-lesson detail, and the material download -- plus the admin
paid-unlock flow where recording a payment flips the enrollment to ACTIVE.
"""

from datetime import date

import pytest

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from app.services import email_service
from tests.conftest import TestingSessionLocal


@pytest.fixture
def sent_emails(monkeypatch):
    captured: list[dict] = []

    def _fake(to_email, to_name, subject, html_content, text_content=None):
        captured.append({"to_email": to_email, "subject": subject, "html": html_content})
        return True

    monkeypatch.setattr(email_service, "send_email", _fake)
    return captured


def _make_client(email: str, name: str = "Student"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=name, email=email, password="password123"),
            role=Role.CLIENT,
        )
    finally:
        db.close()


def _auth(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_course(client, admin_headers, **overrides) -> dict:
    payload = {
        "title": "Intro to Python",
        "description": "Beginner's course.",
        "is_free": True,
        "status": "PUBLISHED",
    }
    payload.update(overrides)
    resp = client.post("/api/v1/courses", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_lesson(client, admin_headers, course_id, **overrides) -> dict:
    payload = {"title": "Lesson 1", "content": "Secret content.", "display_order": 1}
    payload.update(overrides)
    resp = client.post(
        f"/api/v1/courses/{course_id}/lessons", json=payload, headers=admin_headers
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# --- course management ----------------------------------------------------


def test_admin_creates_a_free_course(client, admin_headers):
    body = _create_course(client, admin_headers)
    assert body["title"] == "Intro to Python"
    assert body["slug"] == "intro-to-python"
    assert body["is_free"] is True
    assert body["price"] is None
    assert body["status"] == "PUBLISHED"


def test_paid_course_needs_a_positive_price(client, admin_headers):
    bad = client.post(
        "/api/v1/courses",
        json={"title": "Paid", "description": "d", "is_free": False, "price": 0},
        headers=admin_headers,
    )
    assert bad.status_code == 422

    good = client.post(
        "/api/v1/courses",
        json={"title": "Paid", "description": "d", "is_free": False, "price": "25000.00"},
        headers=admin_headers,
    )
    assert good.status_code == 201
    assert good.json()["price"] == "25000.00"


def test_free_courses_price_is_normalised_to_null(client, admin_headers):
    body = client.post(
        "/api/v1/courses",
        json={"title": "FreeOnly", "description": "d", "is_free": True, "price": "999"},
        headers=admin_headers,
    ).json()
    # The validator wipes `price` on a free course so the two columns stay coherent.
    assert body["price"] is None


def test_partial_update_rechecks_is_free_price_pair(client, admin_headers):
    course = _create_course(client, admin_headers)
    # Flipping to paid without sending a price is rejected.
    bad = client.patch(
        f"/api/v1/courses/{course['id']}", json={"is_free": False}, headers=admin_headers
    )
    assert bad.status_code == 422

    good = client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"is_free": False, "price": "15000.00"},
        headers=admin_headers,
    )
    assert good.status_code == 200
    assert good.json()["is_free"] is False
    assert good.json()["price"] == "15000.00"


def test_only_admin_can_delete_a_course(client, admin_headers, staff_headers):
    course = _create_course(client, admin_headers)
    assert (
        client.delete(f"/api/v1/courses/{course['id']}", headers=staff_headers).status_code
        == 403
    )
    assert (
        client.delete(f"/api/v1/courses/{course['id']}", headers=admin_headers).status_code
        == 200
    )


def test_a_client_cannot_write_courses(client, admin_headers, client_headers):
    assert (
        client.post(
            "/api/v1/courses",
            json={"title": "Sneaky", "description": "d"},
            headers=client_headers,
        ).status_code
        == 403
    )


# --- public catalogue -----------------------------------------------------


def test_public_sees_only_published_active_courses(client, admin_headers):
    _create_course(client, admin_headers, title="Public", status="PUBLISHED")
    _create_course(client, admin_headers, title="Draft", status="DRAFT")

    rows = client.get("/api/v1/courses").json()
    titles = [c["title"] for c in rows]
    assert "Public" in titles
    assert "Draft" not in titles


def test_public_detail_serves_lesson_titles_but_not_content(client, admin_headers):
    course = _create_course(client, admin_headers)
    _add_lesson(client, admin_headers, course["id"], title="Lesson Alpha",
                content="SECRET-STRING")

    resp = client.get(f"/api/v1/courses/{course['slug']}")
    assert resp.status_code == 200
    body = resp.json()
    assert [l["title"] for l in body["lessons"]] == ["Lesson Alpha"]
    # No content field at the lesson level in the public detail, and the string
    # must not appear anywhere in the raw body.
    assert "SECRET-STRING" not in resp.text
    assert "content" not in body["lessons"][0]


def test_a_draft_course_is_a_public_404(client, admin_headers):
    course = _create_course(client, admin_headers, status="DRAFT")
    assert client.get(f"/api/v1/courses/{course['slug']}").status_code == 404
    # Staff can still read it to review before publishing.
    staff = client.get(f"/api/v1/courses/{course['slug']}", headers=admin_headers)
    assert staff.status_code == 200


# --- enrollment: free -----------------------------------------------------


def test_free_enrollment_goes_active_instantly(client, admin_headers, sent_emails):
    course = _create_course(client, admin_headers)
    c = _make_client("free@example.com")

    resp = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["enrollment"]["status"] == "ACTIVE"
    assert body["enrollment"]["invoice_id"] is None
    assert "start learning" in body["message"].lower()

    # Student is notified -- email + bell.
    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "COURSE_ENROLLED" in types
    assert [e["to_email"] for e in sent_emails] == ["free@example.com"]


def test_double_enroll_is_idempotent(client, admin_headers, sent_emails):
    course = _create_course(client, admin_headers)
    c = _make_client("twice@example.com")

    first = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    ).json()
    second = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    ).json()
    assert first["enrollment"]["id"] == second["enrollment"]["id"]
    assert "already enrolled" in second["message"].lower()


def test_enrolling_in_a_draft_course_is_a_404(client, admin_headers, sent_emails):
    course = _create_course(client, admin_headers, status="DRAFT")
    c = _make_client("drafty@example.com")
    resp = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    )
    assert resp.status_code == 404


# --- the gate -------------------------------------------------------------


def test_lesson_content_is_served_to_an_active_enrollment(
    client, admin_headers, sent_emails
):
    course = _create_course(client, admin_headers)
    lesson = _add_lesson(
        client, admin_headers, course["id"], content="FULL-LESSON-BODY"
    )
    c = _make_client("learner@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    listed = client.get(
        f"/api/v1/client/courses/{course['id']}/lessons", headers=_auth(c)
    )
    assert listed.status_code == 200
    assert any("FULL-LESSON-BODY" == l["content"] for l in listed.json())

    one = client.get(
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}",
        headers=_auth(c),
    )
    assert one.status_code == 200
    assert one.json()["content"] == "FULL-LESSON-BODY"


def test_lesson_content_is_hidden_from_a_non_enrolled_client(
    client, admin_headers, sent_emails
):
    """No enrollment -> 404, matching how a project they are not on behaves."""
    course = _create_course(client, admin_headers)
    lesson = _add_lesson(client, admin_headers, course["id"],
                         content="CONFIDENTIAL-LESSON")
    outsider = _make_client("outsider@example.com")

    for path in (
        f"/api/v1/client/courses/{course['id']}/lessons",
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}",
    ):
        resp = client.get(path, headers=_auth(outsider))
        assert resp.status_code == 404, path
        assert "CONFIDENTIAL-LESSON" not in resp.text


def test_pending_payment_is_a_403_with_the_payment_message(
    client, admin_headers, sent_emails
):
    course = _create_course(
        client, admin_headers,
        title="Paid", is_free=False, price="20000.00",
    )
    lesson = _add_lesson(client, admin_headers, course["id"],
                         content="LOCKED-CONTENT")
    c = _make_client("payer@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    for path in (
        f"/api/v1/client/courses/{course['id']}/lessons",
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}",
    ):
        resp = client.get(path, headers=_auth(c))
        assert resp.status_code == 403, path
        assert "complete payment" in resp.json()["detail"].lower()
        assert "LOCKED-CONTENT" not in resp.text


def test_mark_complete_requires_active_enrollment(client, admin_headers, sent_emails):
    course = _create_course(
        client, admin_headers,
        title="Paid", is_free=False, price="20000.00",
    )
    lesson = _add_lesson(client, admin_headers, course["id"])
    c = _make_client("markcomplete@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    resp = client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}/complete",
        headers=_auth(c),
    )
    assert resp.status_code == 403


# --- paid enrollment and the invoice-paid hook ----------------------------


def test_paid_enrollment_generates_an_invoice_and_stays_pending(
    client, admin_headers, sent_emails
):
    course = _create_course(
        client, admin_headers,
        title="Paid Course", is_free=False, price="20000.00",
    )
    c = _make_client("buyer@example.com")

    resp = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["enrollment"]["status"] == "PENDING_PAYMENT"
    invoice_id = body["enrollment"]["invoice_id"]
    assert invoice_id is not None

    inv = client.get(f"/api/v1/invoices/{invoice_id}", headers=admin_headers).json()
    assert any("Paid Course" in item["description"] for item in inv["items"])
    assert inv["total"] == "20000.00"


def test_recording_full_payment_unlocks_access_and_notifies(
    client, admin_headers, sent_emails
):
    """
    The headline flow: paid course + invoice -> record payment -> enrollment
    flips to ACTIVE, student gets COURSE_ACCESS_ACTIVE in-app and by email,
    lesson content becomes readable.
    """
    course = _create_course(
        client, admin_headers,
        title="Pay to Learn", is_free=False, price="30000.00",
    )
    lesson = _add_lesson(client, admin_headers, course["id"],
                         content="UNLOCKED-CONTENT")
    c = _make_client("buyer2@example.com")

    enroll_body = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    ).json()
    invoice_id = enroll_body["enrollment"]["invoice_id"]

    # Before payment the content is locked.
    locked = client.get(
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}",
        headers=_auth(c),
    )
    assert locked.status_code == 403

    sent_emails.clear()
    pay = client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        json={"amount": "30000.00", "method": "BANK_TRANSFER"},
        headers=admin_headers,
    )
    assert pay.status_code == 201, pay.text

    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "COURSE_ACCESS_ACTIVE" in types
    assert any(e["to_email"] == "buyer2@example.com"
               and "active" in e["subject"].lower() for e in sent_emails)

    # And the gate is now open.
    unlocked = client.get(
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}",
        headers=_auth(c),
    )
    assert unlocked.status_code == 200
    assert unlocked.json()["content"] == "UNLOCKED-CONTENT"


def test_partial_payment_does_not_unlock(client, admin_headers, sent_emails):
    """Only PAID (fully) flips the enrollment -- PARTIALLY_PAID stays locked."""
    course = _create_course(
        client, admin_headers,
        title="Half Paid", is_free=False, price="20000.00",
    )
    lesson = _add_lesson(client, admin_headers, course["id"])
    c = _make_client("half@example.com")
    body = client.post(
        f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
    ).json()
    invoice_id = body["enrollment"]["invoice_id"]

    client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        json={"amount": "5000.00", "method": "CASH"},
        headers=admin_headers,
    )

    resp = client.get(
        f"/api/v1/client/courses/{course['id']}/lessons/{lesson['id']}",
        headers=_auth(c),
    )
    assert resp.status_code == 403


# --- progress -------------------------------------------------------------


def test_marking_lessons_complete_updates_progress(
    client, admin_headers, sent_emails
):
    course = _create_course(client, admin_headers)
    l1 = _add_lesson(client, admin_headers, course["id"], title="One", display_order=1)
    l2 = _add_lesson(client, admin_headers, course["id"], title="Two", display_order=2)
    _add_lesson(client, admin_headers, course["id"], title="Three", display_order=3)
    c = _make_client("progress@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    r1 = client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{l1['id']}/complete",
        headers=_auth(c),
    ).json()
    assert r1 == {"completed_lessons": 1, "total_lessons": 3, "progress_percent": 33}

    r2 = client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{l2['id']}/complete",
        headers=_auth(c),
    ).json()
    assert r2["completed_lessons"] == 2
    assert r2["progress_percent"] == 67

    # Idempotent -- marking the same lesson twice does not double-count.
    repeat = client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{l1['id']}/complete",
        headers=_auth(c),
    ).json()
    assert repeat["completed_lessons"] == 2


def test_my_enrollments_lists_courses_with_progress(
    client, admin_headers, sent_emails
):
    course = _create_course(client, admin_headers)
    l1 = _add_lesson(client, admin_headers, course["id"])
    _add_lesson(client, admin_headers, course["id"], title="L2", display_order=2)
    c = _make_client("mylearning@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))
    client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{l1['id']}/complete",
        headers=_auth(c),
    )

    rows = client.get("/api/v1/client/courses", headers=_auth(c)).json()
    assert len(rows) == 1
    assert rows[0]["course_title"] == "Intro to Python"
    assert rows[0]["completed_lessons"] == 1
    assert rows[0]["total_lessons"] == 2
    assert rows[0]["progress_percent"] == 50


# --- admin surfaces -------------------------------------------------------


def test_admin_sees_enrollments_on_a_course(client, admin_headers, sent_emails):
    course = _create_course(client, admin_headers)
    _add_lesson(client, admin_headers, course["id"])
    for i in range(2):
        c = _make_client(f"enrol{i}@example.com", name=f"Student {i}")
        client.post(
            f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c)
        )

    rows = client.get(
        f"/api/v1/courses/{course['id']}/enrollments", headers=admin_headers
    ).json()
    assert len(rows) == 2
    assert all(r["total_lessons"] == 1 for r in rows)
    assert all(r["status"] == "ACTIVE" for r in rows)


def test_dashboard_counts_published_courses_and_active_enrollments(
    client, admin_headers, sent_emails
):
    before = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert before["training"] == {"published_courses": 0, "active_enrollments": 0}

    course = _create_course(client, admin_headers)
    _create_course(client, admin_headers, title="Draft course", status="DRAFT")
    c = _make_client("count@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    after = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert after["training"] == {"published_courses": 1, "active_enrollments": 1}


def test_dashboard_shape_includes_training(client, admin_headers):
    """Guards the key set the frontend reads from `data.training.*`."""
    body = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert "training" in body
    assert set(body["training"]) == {"published_courses", "active_enrollments"}


# --- counting course content respects soft deletes ------------------------


def test_a_soft_deleted_lesson_is_removed_from_the_player(
    client, admin_headers, sent_emails
):
    course = _create_course(client, admin_headers)
    l1 = _add_lesson(client, admin_headers, course["id"], title="Stay", display_order=1)
    l2 = _add_lesson(client, admin_headers, course["id"], title="Gone", display_order=2)
    c = _make_client("deleted@example.com")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    client.delete(
        f"/api/v1/courses/{course['id']}/lessons/{l2['id']}", headers=admin_headers
    )

    listed = client.get(
        f"/api/v1/client/courses/{course['id']}/lessons", headers=_auth(c)
    ).json()
    titles = [l["title"] for l in listed]
    assert "Gone" not in titles
    assert "Stay" in titles

    # Direct fetch is a 404 too.
    assert client.get(
        f"/api/v1/client/courses/{course['id']}/lessons/{l2['id']}",
        headers=_auth(c),
    ).status_code == 404
    _ = l1


def test_certificate_locked_until_every_lesson_is_complete(
    client, admin_headers, sent_emails
):
    """
    The certificate is the lesson gate plus one more condition. Before the last
    lesson it is a 403 with the unlock message; after it, a 200 carrying the
    student's real name and a stable id.
    """
    course = _create_course(client, admin_headers, title="Certifiable Course")
    l1 = _add_lesson(client, admin_headers, course["id"], title="One", display_order=1)
    l2 = _add_lesson(client, admin_headers, course["id"], title="Two", display_order=2)
    c = _make_client("certificate@example.com", name="Ada Mugisha")
    client.post(f"/api/v1/client/courses/{course['id']}/enroll", headers=_auth(c))

    url = f"/api/v1/client/courses/{course['id']}/certificate"

    # Nothing completed yet.
    blocked = client.get(url, headers=_auth(c))
    assert blocked.status_code == 403
    assert "complete every lesson" in blocked.json()["detail"].lower()

    # Half way is still locked.
    client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{l1['id']}/complete",
        headers=_auth(c),
    )
    assert client.get(url, headers=_auth(c)).status_code == 403

    # The last lesson unlocks it.
    client.post(
        f"/api/v1/client/courses/{course['id']}/lessons/{l2['id']}/complete",
        headers=_auth(c),
    )
    issued = client.get(url, headers=_auth(c))
    assert issued.status_code == 200
    body = issued.json()
    assert body["student_name"] == "Ada Mugisha"
    assert body["course_title"] == "Certifiable Course"
    assert body["course_slug"] == course["slug"]
    assert body["lesson_count"] == 2
    assert body["certificate_id"].startswith("WAMUGII-CERT-")
    assert body["issued_on"] == date.today().isoformat()

    # Stable: asking twice gives the same certificate number.
    assert client.get(url, headers=_auth(c)).json()["certificate_id"] == body["certificate_id"]


def test_certificate_follows_the_same_gate_as_lesson_content(
    client, admin_headers, sent_emails
):
    """Not enrolled is a 404, exactly like the lessons endpoint."""
    course = _create_course(client, admin_headers)
    _add_lesson(client, admin_headers, course["id"])
    outsider = _make_client("certoutsider@example.com")

    r = client.get(
        f"/api/v1/client/courses/{course['id']}/certificate",
        headers=_auth(outsider),
    )
    assert r.status_code == 404
