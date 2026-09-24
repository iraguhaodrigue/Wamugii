import pytest

from app.core.config import settings
from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from app.services import email_service
from tests.conftest import TestingSessionLocal


@pytest.fixture
def sent_emails(monkeypatch):
    """
    Capture outbound email instead of calling Brevo.

    Patches the attribute on the module rather than the name imported into
    notifications.py — notifications.py calls `email_service.send_email(...)`,
    so the lookup happens at call time and this patch takes effect.
    """
    captured: list[dict] = []

    def _fake_send_email(to_email, to_name, subject, html_content, text_content=None):
        captured.append(
            {
                "to_email": to_email,
                "to_name": to_name,
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }
        )
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send_email)
    return captured


def _create_client(email: str, full_name: str = "Email Client"):
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


def _subjects(captured) -> list[str]:
    return [e["subject"] for e in captured]


def _to(captured) -> list[str]:
    return [e["to_email"] for e in captured]


# --- events that should email ----------------------------------------------


def test_quote_submitted_emails_staff_and_admin(client, admin_headers, staff_headers, sent_emails):
    resp = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Walk-in Lead",
            "email": "lead@example.com",
            "phone": "0700000000",
            "project_title": "Shop website",
            "project_description": "A site for my shop",
        },
    )
    assert resp.status_code == 201

    # conftest creates admin@example.com / staff@example.com for those fixtures.
    assert "admin@example.com" in _to(sent_emails)
    assert "staff@example.com" in _to(sent_emails)
    assert all(s == "New Quote Request — Shop website" for s in _subjects(sent_emails))
    # The submitter's own details belong in the body, not the recipient list.
    assert "lead@example.com" not in _to(sent_emails)
    assert "lead@example.com" in sent_emails[0]["html"]


def test_project_status_change_emails_the_client(client, admin_headers, sent_emails):
    c = _create_client("email_projstatus@example.com")
    project = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Status Project", "description": "d"},
        headers=admin_headers,
    ).json()
    sent_emails.clear()  # PROJECT_CREATED is in-app only

    client.patch(
        f"/api/v1/projects/{project['id']}", json={"status": "IN_PROGRESS"}, headers=admin_headers
    )

    assert _to(sent_emails) == ["email_projstatus@example.com"]
    assert _subjects(sent_emails) == ["Your Project 'Status Project' has been updated"]
    # Plain-English meaning, not a raw enum.
    assert "We've started working on your project" in sent_emails[0]["html"]


def test_milestone_completion_emails_the_client(client, admin_headers, sent_emails):
    c = _create_client("email_milestone@example.com")
    project = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Milestone Project", "description": "d"},
        headers=admin_headers,
    ).json()
    milestone = client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Phase 1", "description": "first"},
        headers=admin_headers,
    ).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )

    assert _to(sent_emails) == ["email_milestone@example.com"]
    assert _subjects(sent_emails) == ["Milestone Completed: Phase 1"]


def test_issued_invoice_emails_the_client(client, admin_headers, sent_emails):
    c = _create_client("email_invoice@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "1000.00", "tax_rate": "18", "status": "SENT"},
        headers=admin_headers,
    ).json()

    assert _to(sent_emails) == ["email_invoice@example.com"]
    assert _subjects(sent_emails) == [
        f"Invoice {invoice['invoice_number']} from WAMUGII TECH SOLUTIONS"
    ]
    html = sent_emails[0]["html"]
    assert "RWF 1180.00" in html
    assert "VAT (18.00%)" in html
    # Never imply the client can pay online.
    assert "pay online" not in html.lower()


def test_draft_invoice_does_not_email(client, admin_headers, sent_emails):
    """A draft isn't issued to the client, so it must not reach their inbox."""
    c = _create_client("email_draft@example.com")
    client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "DRAFT"},
        headers=admin_headers,
    )
    assert sent_emails == []


def test_payment_recorded_emails_the_client(client, admin_headers, sent_emails):
    c = _create_client("email_payment@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "1000.00", "status": "SENT"},
        headers=admin_headers,
    ).json()
    sent_emails.clear()  # drop the INVOICE_CREATED email

    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "400.00", "method": "MOBILE_MONEY"},
        headers=admin_headers,
    )

    assert _to(sent_emails) == ["email_payment@example.com"]
    assert _subjects(sent_emails) == [f"Payment Received — {invoice['invoice_number']}"]
    html = sent_emails[0]["html"]
    assert "RWF 400.00" in html
    assert "Mobile Money" in html  # method, humanised
    assert "RWF 600.00" in html  # new balance due


# --- events that should NOT email -------------------------------------------


def test_quote_status_change_does_not_email(client, admin_headers, sent_emails):
    """In-app only — staff change these often and it would be noise."""
    _create_client("email_quotestatus@example.com")
    quote = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Quote Client",
            "email": "email_quotestatus@example.com",
            "phone": "0700000000",
            "project_title": "Quoted work",
            "project_description": "details",
        },
    ).json()
    sent_emails.clear()  # drop the QUOTE_SUBMITTED staff emails

    client.patch(
        f"/api/v1/quote-requests/{quote['id']}", json={"status": "REVIEWING"}, headers=admin_headers
    )
    assert sent_emails == []


def test_project_creation_does_not_email(client, admin_headers, sent_emails):
    c = _create_client("email_projcreate@example.com")
    client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Quiet", "description": "d"},
        headers=admin_headers,
    )
    assert sent_emails == []


# --- the non-fatal contract -------------------------------------------------


def test_unconfigured_brevo_skips_sending_and_action_succeeds(client, admin_headers, monkeypatch):
    """
    With no API key, send_email is a graceful no-op: it returns False without
    touching the network, and the payment still goes through.
    """
    monkeypatch.setattr(settings, "BREVO_API_KEY", None)
    monkeypatch.setattr(settings, "BREVO_FROM_EMAIL", None)

    def _explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("httpx.post must not be called when Brevo is unconfigured")

    monkeypatch.setattr("app.services.email_service.httpx.post", _explode)

    assert email_service.is_configured() is False
    assert email_service.send_email("a@b.com", "A", "s", "<p>h</p>") is False

    c = _create_client("email_unconfigured@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()
    resp = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "500.00", "method": "CASH"},
        headers=admin_headers,
    )
    assert resp.status_code == 201

    after = client.get(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers).json()
    assert after["amount_paid"] == "500.00"
    assert after["status"] == "PAID"
    # The in-app notification still landed.
    notes = client.get("/api/v1/notifications", headers=_auth(c)).json()
    assert any(n["type"] == "PAYMENT_RECORDED" for n in notes)


def test_email_failure_does_not_break_the_action(client, admin_headers, monkeypatch):
    """A raising send_email must not disturb the payment or the notification."""
    def _boom(*args, **kwargs):
        raise RuntimeError("Brevo exploded")

    monkeypatch.setattr(email_service, "send_email", _boom)

    c = _create_client("email_failsafe@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()
    resp = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "200.00", "method": "CASH"},
        headers=admin_headers,
    )
    assert resp.status_code == 201

    after = client.get(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers).json()
    assert after["amount_paid"] == "200.00"
    assert after["status"] == "PARTIALLY_PAID"
    notes = client.get("/api/v1/notifications", headers=_auth(c)).json()
    assert any(n["type"] == "PAYMENT_RECORDED" for n in notes)


# --- send_email itself ------------------------------------------------------


def test_send_email_posts_to_brevo_and_reports_success(monkeypatch):
    monkeypatch.setattr(settings, "BREVO_API_KEY", "test-key")
    monkeypatch.setattr(settings, "BREVO_FROM_EMAIL", "noreply@wamugii.test")
    calls: list[dict] = []

    class _Response:
        is_success = True
        status_code = 201
        text = ""

    def _fake_post(url, json=None, headers=None, timeout=None):
        calls.append({"url": url, "json": json, "headers": headers})
        return _Response()

    monkeypatch.setattr("app.services.email_service.httpx.post", _fake_post)

    assert email_service.send_email("c@example.com", "C", "Subject", "<p>Hi</p>", "Hi") is True
    assert calls[0]["url"] == "https://api.brevo.com/v3/smtp/email"
    assert calls[0]["headers"]["api-key"] == "test-key"
    assert calls[0]["json"]["sender"]["email"] == "noreply@wamugii.test"
    assert calls[0]["json"]["to"] == [{"email": "c@example.com", "name": "C"}]
    assert calls[0]["json"]["textContent"] == "Hi"


def test_send_email_returns_false_on_rejection_and_on_network_error(monkeypatch):
    monkeypatch.setattr(settings, "BREVO_API_KEY", "test-key")
    monkeypatch.setattr(settings, "BREVO_FROM_EMAIL", "noreply@wamugii.test")

    class _Rejected:
        is_success = False
        status_code = 401
        text = "unauthorized"

    monkeypatch.setattr(
        "app.services.email_service.httpx.post", lambda *a, **k: _Rejected()
    )
    assert email_service.send_email("c@example.com", "C", "S", "<p>h</p>") is False

    def _network_error(*args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr("app.services.email_service.httpx.post", _network_error)
    assert email_service.send_email("c@example.com", "C", "S", "<p>h</p>") is False


def test_cta_button_omitted_without_frontend_url(monkeypatch):
    """No FRONTEND_URL means no button, rather than a dead localhost link."""
    from app.services import email_templates

    monkeypatch.setattr(settings, "FRONTEND_URL", None)
    assert email_templates._cta_url("/client/invoices/1") is None
    assert email_templates._button(None, "View Invoice") == ""

    monkeypatch.setattr(settings, "FRONTEND_URL", "https://wamugii.test/")
    assert email_templates._cta_url("/client/invoices/1") == "https://wamugii.test/client/invoices/1"
    assert "https://wamugii.test/client/invoices/1" in email_templates._button(
        email_templates._cta_url("/client/invoices/1"), "View Invoice"
    )
