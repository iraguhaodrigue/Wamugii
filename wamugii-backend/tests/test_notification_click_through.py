"""
Notification click-through: the contract the frontend bell depends on.

The bell turns `related_type` + `related_id` into a URL, so a notification with
the wrong pair (or a missing one) is a dead click even though the notification
itself looks fine. The existing suites assert the *type* of each notification
and who gets emailed; these tests assert the pair, and then fetch the
client-facing resource it points at to prove the destination really resolves
for that client.
"""

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


def _make_client(email: str, full_name: str = "Click Client"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password="password123"),
            role=Role.CLIENT,
        )
    finally:
        db.close()


def _auth(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _notifications(client, user) -> list[dict]:
    return client.get("/api/v1/notifications", headers=_auth(user)).json()


def _latest(notifications: list[dict], type_: str) -> dict:
    matches = [n for n in notifications if n["type"] == type_]
    assert matches, f"no {type_} notification was emitted"
    return matches[0]


# --- tickets ----------------------------------------------------------------


def test_staff_reply_points_the_client_at_their_ticket(client, admin_headers, sent_emails):
    """The headline flow: client opens a ticket, staff replies, client clicks."""
    c = _make_client("click_ticket@example.com")
    ticket = client.post(
        "/api/v1/client/tickets",
        json={"subject": "Site is down", "description": "It won't load."},
        headers=_auth(c),
    ).json()
    sent_emails.clear()

    reply = client.post(
        f"/api/v1/tickets/{ticket['id']}/messages",
        json={"message": "Back up now — please confirm."},
        headers=admin_headers,
    )
    assert reply.status_code == 201

    note = _latest(_notifications(client, c), "TICKET_REPLY")
    assert note["related_type"] == "ticket"
    assert note["related_id"] == ticket["id"]

    # The email goes to the client, not to us.
    assert [e["to_email"] for e in sent_emails] == ["click_ticket@example.com"]

    # And the destination that pair resolves to is readable by this client,
    # with the reply in the thread.
    detail = client.get(f"/api/v1/client/tickets/{note['related_id']}", headers=_auth(c))
    assert detail.status_code == 200
    assert [m["message"] for m in detail.json()["messages"]] == ["Back up now — please confirm."]


def test_an_internal_note_creates_no_client_click_through(client, admin_headers, sent_emails):
    """A staff-only note must not produce a notification the client can click."""
    c = _make_client("click_note@example.com")
    ticket = client.post(
        "/api/v1/client/tickets",
        json={"subject": "Quiet", "description": "d"},
        headers=_auth(c),
    ).json()
    sent_emails.clear()

    client.post(
        f"/api/v1/tickets/{ticket['id']}/messages",
        json={"message": "Client is behind on payment — go gently.", "is_internal_note": True},
        headers=admin_headers,
    )

    assert "TICKET_REPLY" not in [n["type"] for n in _notifications(client, c)]
    assert sent_emails == []


@pytest.mark.parametrize("status", ["RESOLVED", "CLOSED", "WAITING_ON_CLIENT"])
def test_status_change_points_the_client_at_their_ticket(
    client, admin_headers, sent_emails, status
):
    c = _make_client(f"click_status_{status.lower()}@example.com")
    ticket = client.post(
        "/api/v1/client/tickets",
        json={"subject": "Status", "description": "d"},
        headers=_auth(c),
    ).json()

    client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": status}, headers=admin_headers)

    note = _latest(_notifications(client, c), "TICKET_STATUS_CHANGED")
    assert note["related_type"] == "ticket"
    assert note["related_id"] == ticket["id"]
    assert client.get(
        f"/api/v1/client/tickets/{note['related_id']}", headers=_auth(c)
    ).status_code == 200


def test_client_reply_points_staff_at_the_staff_view(client, admin_headers, sent_emails):
    """The mirror direction — staff get the same pair, resolved on /tickets."""
    c = _make_client("click_to_staff@example.com")
    ticket = client.post(
        "/api/v1/client/tickets",
        json={"subject": "Following up", "description": "d"},
        headers=_auth(c),
    ).json()
    assert (
        client.post(
            f"/api/v1/client/tickets/{ticket['id']}/messages",
            json={"message": "Any update?"},
            headers=_auth(c),
        ).status_code
        == 201
    )

    db = TestingSessionLocal()
    try:
        admin = user_crud.get_by_email(db, "admin@example.com")
    finally:
        db.close()

    note = _latest(_notifications(client, admin), "TICKET_REPLY")
    assert note["related_type"] == "ticket"
    assert note["related_id"] == ticket["id"]
    assert client.get(
        f"/api/v1/tickets/{note['related_id']}", headers=admin_headers
    ).status_code == 200


# --- quotes -----------------------------------------------------------------


def test_quote_status_change_points_the_client_at_their_quote(
    client, admin_headers, sent_emails
):
    c = _make_client("click_quote@example.com")
    quote = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Click Client",
            "email": "click_quote@example.com",
            "phone": "0700000000",
            "project_title": "New website",
            "project_description": "Please build us a marketing site.",
        },
    ).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/quote-requests/{quote['id']}",
        json={"status": "QUOTED"},
        headers=admin_headers,
    )

    note = _latest(_notifications(client, c), "QUOTE_STATUS_CHANGED")
    assert note["related_type"] == "quote"
    assert note["related_id"] == quote["id"]

    detail = client.get(f"/api/v1/client/quotes/{note['related_id']}", headers=_auth(c))
    assert detail.status_code == 200
    assert detail.json()["project_title"] == "New website"


# --- domains ----------------------------------------------------------------


def test_domain_registration_points_the_client_at_their_domain(
    client, admin_headers, sent_emails
):
    c = _make_client("click_domain@example.com")
    domain = client.post(
        "/api/v1/domains",
        json={
            "client_id": c.id,
            "domain_name": "clicksite.rw",
            "registration_fee": "15000.00",
            "service_fee": "5000.00",
        },
        headers=admin_headers,
    ).json()

    note = _latest(_notifications(client, c), "DOMAIN_REGISTERED")
    assert note["related_type"] == "domain"
    assert note["related_id"] == domain["id"]
    assert [e["to_email"] for e in sent_emails] == ["click_domain@example.com"]

    detail = client.get(f"/api/v1/client/domains/{note['related_id']}", headers=_auth(c))
    assert detail.status_code == 200
    assert detail.json()["domain_name"] == "clicksite.rw"


def test_domain_status_change_points_the_client_at_their_domain(
    client, admin_headers, sent_emails
):
    c = _make_client("click_domain_status@example.com")
    domain = client.post(
        "/api/v1/domains",
        json={
            "client_id": c.id,
            "domain_name": "clickactive.rw",
            "registration_fee": "15000.00",
        },
        headers=admin_headers,
    ).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/domains/{domain['id']}",
        json={"status": "ACTIVE"},
        headers=admin_headers,
    )

    note = _latest(_notifications(client, c), "DOMAIN_STATUS_CHANGED")
    assert note["related_type"] == "domain"
    assert note["related_id"] == domain["id"]
    assert client.get(
        f"/api/v1/client/domains/{note['related_id']}", headers=_auth(c)
    ).status_code == 200


# --- hosting ----------------------------------------------------------------


def test_hosting_creation_points_the_client_at_their_account(
    client, admin_headers, sent_emails
):
    """`hosting` was the fourth related_type with no route wired — same contract."""
    c = _make_client("click_hosting@example.com")
    plan = client.post(
        "/api/v1/hosting/plans",
        json={
            "name": "Click Plan",
            "features": "1 site",
            "monthly_price": "10000.00",
            "yearly_price": "100000.00",
            "display_order": 1,
            "is_active": True,
        },
        headers=admin_headers,
    ).json()
    account = client.post(
        "/api/v1/hosting/accounts",
        json={"client_id": c.id, "plan_id": plan["id"], "billing_cycle": "MONTHLY"},
        headers=admin_headers,
    ).json()

    note = _latest(_notifications(client, c), "HOSTING_ACCOUNT_CREATED")
    assert note["related_type"] == "hosting"
    assert note["related_id"] == account["id"]
    assert client.get(
        f"/api/v1/client/hosting/{note['related_id']}", headers=_auth(c)
    ).status_code == 200


def test_quote_status_change_is_in_app_only(client, admin_headers, sent_emails):
    """
    Pins current behaviour, which is *not* the same as the other client-facing
    status changes: there is no `quote_status_changed_client` template, so the
    client gets a bell notification and no email. Every other client-facing
    transition (ticket, domain, hosting, project) emails as well. If a template
    is added later, this test should flip rather than quietly start passing for
    the wrong reason.
    """
    c = _make_client("click_quote_noemail@example.com")
    quote = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Click Client",
            "email": "click_quote_noemail@example.com",
            "phone": "0700000000",
            "project_title": "Another site",
            "project_description": "d",
        },
    ).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/quote-requests/{quote['id']}",
        json={"status": "ACCEPTED"},
        headers=admin_headers,
    )

    assert "QUOTE_STATUS_CHANGED" in [n["type"] for n in _notifications(client, c)]
    assert sent_emails == []
