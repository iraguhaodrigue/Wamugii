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

    def _fake_send_email(to_email, to_name, subject, html_content, text_content=None):
        captured.append({"to_email": to_email, "subject": subject, "html": html_content})
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send_email)
    return captured


def _make_user(email: str, role: Role = Role.CLIENT, full_name: str = "Support User"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password="password123"),
            role=role,
        )
    finally:
        db.close()


def _auth(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _open_ticket(client, headers, **overrides):
    payload = {"subject": "Site is down", "description": "My website won't load."}
    payload.update(overrides)
    return client.post("/api/v1/client/tickets", json=payload, headers=headers)


def _make_project(client, admin_headers, client_id: int, title="Ticket Project"):
    return client.post(
        "/api/v1/projects",
        json={"client_id": client_id, "title": title, "description": "d"},
        headers=admin_headers,
    ).json()


# --- creation ---------------------------------------------------------------


def test_client_opens_a_ticket(client, admin_headers, sent_emails):
    c = _make_user("tkt_create@example.com")
    resp = _open_ticket(client, _auth(c), category="TECHNICAL")
    assert resp.status_code == 201
    body = resp.json()
    assert body["subject"] == "Site is down"
    assert body["status"] == "OPEN"
    assert body["category"] == "TECHNICAL"
    assert body["priority"] == "MEDIUM"
    # The client's view never carries the assignee.
    assert "assigned_to" not in body


def test_ticket_creation_notifies_staff_and_admin(client, admin_headers, staff_headers, sent_emails):
    c = _make_user("tkt_notify@example.com")
    _open_ticket(client, _auth(c))

    for headers in (admin_headers, staff_headers):
        types = [n["type"] for n in client.get("/api/v1/notifications", headers=headers).json()]
        assert "TICKET_CREATED" in types

    recipients = sorted(e["to_email"] for e in sent_emails)
    assert recipients == ["admin@example.com", "staff@example.com"]
    assert sent_emails[0]["subject"] == "New support ticket — Site is down"


def test_staff_cannot_use_the_client_ticket_endpoint(client, staff_headers):
    assert _open_ticket(client, staff_headers).status_code == 403


def test_anonymous_cannot_open_a_ticket(client):
    assert client.post(
        "/api/v1/client/tickets", json={"subject": "x", "description": "y"}
    ).status_code == 401


def test_project_must_belong_to_the_same_client(client, admin_headers, sent_emails):
    owner = _make_user("tkt_owner@example.com")
    other = _make_user("tkt_other@example.com")
    project = _make_project(client, admin_headers, owner.id)

    # Someone else's project is rejected...
    mismatch = _open_ticket(client, _auth(other), project_id=project["id"])
    assert mismatch.status_code == 422
    assert "different client" in mismatch.json()["detail"]

    # ...their own is accepted.
    ok = _open_ticket(client, _auth(owner), project_id=project["id"])
    assert ok.status_code == 201
    assert ok.json()["project_id"] == project["id"]


def test_staff_can_raise_a_ticket_for_a_client(client, admin_headers, sent_emails):
    c = _make_user("tkt_onbehalf@example.com")
    resp = client.post(
        "/api/v1/tickets",
        json={
            "client_id": c.id,
            "subject": "Raised by staff",
            "description": "Called in by phone",
            "priority": "HIGH",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["priority"] == "HIGH"
    assert resp.json()["client_id"] == c.id


# --- client scoping ---------------------------------------------------------


def test_client_sees_only_their_own_tickets(client, admin_headers, sent_emails):
    c1 = _make_user("tkt_mine@example.com")
    c2 = _make_user("tkt_theirs@example.com")
    mine = _open_ticket(client, _auth(c1), subject="Mine").json()
    _open_ticket(client, _auth(c2), subject="Theirs")

    listed = client.get("/api/v1/client/tickets", headers=_auth(c1)).json()
    assert [t["id"] for t in listed] == [mine["id"]]
    assert [t["subject"] for t in listed] == ["Mine"]


def test_cross_client_ticket_detail_returns_404(client, admin_headers, sent_emails):
    c1 = _make_user("tkt_a@example.com")
    c2 = _make_user("tkt_b@example.com")
    theirs = _open_ticket(client, _auth(c1)).json()

    assert client.get(f"/api/v1/client/tickets/{theirs['id']}", headers=_auth(c2)).status_code == 404
    # ...and they can't reply into it either.
    assert client.post(
        f"/api/v1/client/tickets/{theirs['id']}/messages",
        json={"message": "sneaking in"},
        headers=_auth(c2),
    ).status_code == 404


def test_client_cannot_reach_the_staff_ticket_endpoints(client, sent_emails):
    c = _make_user("tkt_denied@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    assert client.get("/api/v1/tickets", headers=_auth(c)).status_code == 403
    assert client.get(f"/api/v1/tickets/{ticket['id']}", headers=_auth(c)).status_code == 403
    assert client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"status": "CLOSED"}, headers=_auth(c)
    ).status_code == 403


# --- internal notes ---------------------------------------------------------


def test_internal_notes_never_reach_the_client(client, admin_headers, sent_emails):
    """The most important leak check in this module."""
    c = _make_user("tkt_internal@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    SECRET = "Client is on a payment plan — do not escalate. INTERNAL"

    client.post(
        f"/api/v1/tickets/{ticket['id']}/messages",
        json={"message": SECRET, "is_internal_note": True},
        headers=admin_headers,
    )
    client.post(
        f"/api/v1/tickets/{ticket['id']}/messages",
        json={"message": "We're looking into it now."},
        headers=admin_headers,
    )

    # Staff see both.
    staff_view = client.get(f"/api/v1/tickets/{ticket['id']}", headers=admin_headers).json()
    assert len(staff_view["messages"]) == 2
    assert any(m["is_internal_note"] for m in staff_view["messages"])
    assert SECRET in str(staff_view)

    # The client sees only the real reply.
    detail = client.get(f"/api/v1/client/tickets/{ticket['id']}", headers=_auth(c))
    body = detail.json()
    assert len(body["messages"]) == 1
    assert body["messages"][0]["message"] == "We're looking into it now."
    assert SECRET not in detail.text
    assert "is_internal_note" not in body["messages"][0]


def test_an_internal_note_does_not_email_the_client(client, admin_headers, sent_emails):
    c = _make_user("tkt_nomail@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    sent_emails.clear()

    client.post(
        f"/api/v1/tickets/{ticket['id']}/messages",
        json={"message": "internal only", "is_internal_note": True},
        headers=admin_headers,
    )
    assert sent_emails == []
    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "TICKET_REPLY" not in types


def test_a_client_cannot_post_an_internal_note(client, admin_headers, sent_emails):
    """`is_internal_note` in the body is ignored on the client endpoint."""
    c = _make_user("tkt_forge@example.com")
    ticket = _open_ticket(client, _auth(c)).json()

    client.post(
        f"/api/v1/client/tickets/{ticket['id']}/messages",
        json={"message": "trying to hide this", "is_internal_note": True},
        headers=_auth(c),
    )

    staff_view = client.get(f"/api/v1/tickets/{ticket['id']}", headers=admin_headers).json()
    posted = [m for m in staff_view["messages"] if m["message"] == "trying to hide this"]
    assert len(posted) == 1
    assert posted[0]["is_internal_note"] is False


# --- replies ----------------------------------------------------------------


def test_staff_reply_notifies_and_emails_the_client(client, admin_headers, sent_emails):
    c = _make_user("tkt_reply@example.com")
    ticket = _open_ticket(client, _auth(c), subject="Need help").json()
    sent_emails.clear()

    resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/messages",
        json={"message": "We've restarted your server — try again."},
        headers=admin_headers,
    )
    assert resp.status_code == 201

    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "TICKET_REPLY" in types

    assert [e["to_email"] for e in sent_emails] == ["tkt_reply@example.com"]
    assert sent_emails[0]["subject"] == "New reply on your support ticket: Need help"
    # The reply body travels in the email so it's readable without logging in.
    assert "restarted your server" in sent_emails[0]["html"]


def test_client_reply_notifies_the_assignee_only(client, admin_headers, staff_headers, sent_emails):
    c = _make_user("tkt_assigned@example.com")
    ticket = _open_ticket(client, _auth(c)).json()

    # Assign to the staff fixture user.
    staff = user_crud_by_email("staff@example.com")
    client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"assigned_to": staff.id}, headers=admin_headers
    )
    sent_emails.clear()

    client.post(
        f"/api/v1/client/tickets/{ticket['id']}/messages",
        json={"message": "Still broken."},
        headers=_auth(c),
    )

    assert [e["to_email"] for e in sent_emails] == ["staff@example.com"]
    staff_types = [n["type"] for n in client.get("/api/v1/notifications", headers=staff_headers).json()]
    assert "TICKET_REPLY" in staff_types


def test_client_reply_fans_out_when_unassigned(client, admin_headers, staff_headers, sent_emails):
    c = _make_user("tkt_unassigned@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    sent_emails.clear()

    client.post(
        f"/api/v1/client/tickets/{ticket['id']}/messages",
        json={"message": "Any update?"},
        headers=_auth(c),
    )
    recipients = sorted(e["to_email"] for e in sent_emails)
    assert recipients == ["admin@example.com", "staff@example.com"]


def test_client_reply_reopens_a_waiting_ticket(client, admin_headers, sent_emails):
    c = _make_user("tkt_waiting@example.com")
    ticket = _open_ticket(client, _auth(c)).json()

    client.patch(
        f"/api/v1/tickets/{ticket['id']}",
        json={"status": "WAITING_ON_CLIENT"},
        headers=admin_headers,
    )
    waiting = client.get(f"/api/v1/client/tickets/{ticket['id']}", headers=_auth(c)).json()
    assert waiting["status"] == "WAITING_ON_CLIENT"

    client.post(
        f"/api/v1/client/tickets/{ticket['id']}/messages",
        json={"message": "Here's the info you asked for."},
        headers=_auth(c),
    )
    after = client.get(f"/api/v1/client/tickets/{ticket['id']}", headers=_auth(c)).json()
    assert after["status"] == "OPEN"


def test_client_reply_does_not_disturb_other_statuses(client, admin_headers, sent_emails):
    c = _make_user("tkt_inprog@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"status": "IN_PROGRESS"}, headers=admin_headers
    )

    client.post(
        f"/api/v1/client/tickets/{ticket['id']}/messages",
        json={"message": "one more thing"},
        headers=_auth(c),
    )
    after = client.get(f"/api/v1/client/tickets/{ticket['id']}", headers=_auth(c)).json()
    assert after["status"] == "IN_PROGRESS"


# --- status changes ---------------------------------------------------------


@pytest.mark.parametrize("status", ["RESOLVED", "CLOSED", "WAITING_ON_CLIENT"])
def test_notifiable_status_changes_reach_the_client(client, admin_headers, sent_emails, status):
    c = _make_user(f"tkt_status_{status.lower()}@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    sent_emails.clear()

    client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": status}, headers=admin_headers)

    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "TICKET_STATUS_CHANGED" in types
    assert [e["to_email"] for e in sent_emails] == [f"tkt_status_{status.lower()}@example.com"]


def test_in_progress_does_not_notify_the_client(client, admin_headers, sent_emails):
    """Internal workflow movement isn't worth an email."""
    c = _make_user("tkt_quiet@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"status": "IN_PROGRESS"}, headers=admin_headers
    )
    assert sent_emails == []


def test_resaving_the_same_status_does_not_renotify(client, admin_headers, sent_emails):
    c = _make_user("tkt_resave@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"status": "RESOLVED"}, headers=admin_headers
    )
    sent_emails.clear()
    client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"status": "RESOLVED"}, headers=admin_headers
    )
    assert sent_emails == []


def test_assignee_must_be_staff_or_admin(client, admin_headers, sent_emails):
    c = _make_user("tkt_badassign@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    resp = client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"assigned_to": c.id}, headers=admin_headers
    )
    assert resp.status_code == 422


# --- soft delete & filters --------------------------------------------------


def test_soft_delete_hides_the_ticket_everywhere(client, admin_headers, sent_emails):
    c = _make_user("tkt_del@example.com")
    ticket = _open_ticket(client, _auth(c)).json()

    deleted = client.delete(f"/api/v1/tickets/{ticket['id']}", headers=admin_headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    assert ticket["id"] not in [
        t["id"] for t in client.get("/api/v1/tickets", headers=admin_headers).json()
    ]
    assert client.get("/api/v1/client/tickets", headers=_auth(c)).json() == []
    assert client.get(f"/api/v1/client/tickets/{ticket['id']}", headers=_auth(c)).status_code == 404


def test_staff_cannot_delete_a_ticket(client, admin_headers, staff_headers, sent_emails):
    c = _make_user("tkt_staffdel@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    assert client.delete(
        f"/api/v1/tickets/{ticket['id']}", headers=staff_headers
    ).status_code == 403


def test_ticket_filters(client, admin_headers, sent_emails):
    c1 = _make_user("tkt_f1@example.com")
    c2 = _make_user("tkt_f2@example.com")
    a = _open_ticket(client, _auth(c1), subject="Alpha billing", category="BILLING").json()
    _open_ticket(client, _auth(c2), subject="Beta technical", category="TECHNICAL")
    client.patch(
        f"/api/v1/tickets/{a['id']}", json={"status": "RESOLVED", "priority": "URGENT"},
        headers=admin_headers,
    )

    def ids(**params):
        return [
            t["id"]
            for t in client.get("/api/v1/tickets", params=params, headers=admin_headers).json()
        ]

    assert ids(status="RESOLVED") == [a["id"]]
    assert ids(priority="URGENT") == [a["id"]]
    assert ids(category="BILLING") == [a["id"]]
    assert ids(client_id=c1.id) == [a["id"]]
    assert ids(search="alpha") == [a["id"]]


# --- dashboard --------------------------------------------------------------


def test_dashboard_open_ticket_count_is_real(client, admin_headers, sent_emails):
    before = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert before["support"] == {"open_tickets": 0}

    c = _make_user("tkt_dash@example.com")
    ticket = _open_ticket(client, _auth(c)).json()
    assert client.get("/api/v1/admin/dashboard", headers=admin_headers).json()["support"][
        "open_tickets"
    ] == 1

    # WAITING_ON_CLIENT still counts as open work.
    client.patch(
        f"/api/v1/tickets/{ticket['id']}",
        json={"status": "WAITING_ON_CLIENT"},
        headers=admin_headers,
    )
    assert client.get("/api/v1/admin/dashboard", headers=admin_headers).json()["support"][
        "open_tickets"
    ] == 1

    # RESOLVED does not.
    client.patch(
        f"/api/v1/tickets/{ticket['id']}", json={"status": "RESOLVED"}, headers=admin_headers
    )
    assert client.get("/api/v1/admin/dashboard", headers=admin_headers).json()["support"][
        "open_tickets"
    ] == 0


def test_dashboard_shape_is_unchanged(client, admin_headers):
    body = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert set(body) == {
        "users", "services", "projects", "quotes", "invoices", "hosting", "store", "support",
    }
    assert set(body["support"]) == {"open_tickets"}


def user_crud_by_email(email: str):
    db = TestingSessionLocal()
    try:
        return user_crud.get_by_email(db, email)
    finally:
        db.close()
