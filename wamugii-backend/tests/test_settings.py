import pytest

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.company_settings import DEFAULT_COMPANY_NAME, DEFAULT_SLOGAN
from app.models.user import Role
from app.schemas.user import UserCreate
from app.services import email_service
from tests.conftest import TestingSessionLocal


@pytest.fixture
def sent_emails(monkeypatch):
    """Capture outbound email instead of calling Brevo (see test_email_notifications)."""
    captured: list[dict] = []

    def _fake_send_email(to_email, to_name, subject, html_content, text_content=None):
        captured.append({"to_email": to_email, "subject": subject, "html": html_content})
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send_email)
    return captured


def _create_client(email: str, full_name: str = "Settings Client"):
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


# --- access control ---------------------------------------------------------


def test_admin_gets_settings_with_defaults(client, admin_headers):
    """First read creates the singleton row with WAMUGII's defaults."""
    resp = client.get("/api/v1/settings", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert body["company_name"] == DEFAULT_COMPANY_NAME
    assert body["slogan"] == DEFAULT_SLOGAN
    assert body["tin"] is None
    assert body["notification_email"] is None


def test_settings_is_a_singleton(client, admin_headers):
    """Repeated reads return the same row rather than creating new ones."""
    first = client.get("/api/v1/settings", headers=admin_headers).json()
    client.patch("/api/v1/settings", json={"tin": "123456789"}, headers=admin_headers)
    second = client.get("/api/v1/settings", headers=admin_headers).json()
    assert first["id"] == second["id"] == 1
    assert second["tin"] == "123456789"


def test_staff_cannot_read_settings(client, staff_headers):
    assert client.get("/api/v1/settings", headers=staff_headers).status_code == 403


def test_client_cannot_read_settings(client, client_headers):
    assert client.get("/api/v1/settings", headers=client_headers).status_code == 403


def test_anonymous_cannot_read_settings(client):
    assert client.get("/api/v1/settings").status_code == 401


def test_only_admin_can_patch_settings(client, staff_headers, client_headers):
    assert client.patch("/api/v1/settings", json={"tin": "1"}, headers=staff_headers).status_code == 403
    assert client.patch("/api/v1/settings", json={"tin": "1"}, headers=client_headers).status_code == 403
    assert client.patch("/api/v1/settings", json={"tin": "1"}).status_code == 401


# --- updating ---------------------------------------------------------------


def test_patch_updates_fields(client, admin_headers):
    resp = client.patch(
        "/api/v1/settings",
        json={
            "company_name": "WAMUGII TECH SOLUTIONS LTD",
            "tin": "102938475",
            "address": "KG 11 Ave, Kigali",
            "phone": "+250788000000",
            "email": "hello@wamugii.rw",
            "website": "https://wamugii.rw",
            "notification_email": "quotes@wamugii.rw",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["company_name"] == "WAMUGII TECH SOLUTIONS LTD"
    assert body["tin"] == "102938475"
    assert body["notification_email"] == "quotes@wamugii.rw"
    assert body["website"] == "https://wamugii.rw"


def test_patch_is_partial(client, admin_headers):
    """Fields not in the request body are left alone."""
    client.patch("/api/v1/settings", json={"tin": "555", "phone": "+250788111111"}, headers=admin_headers)
    after = client.patch(
        "/api/v1/settings", json={"address": "Kigali Heights"}, headers=admin_headers
    ).json()
    assert after["address"] == "Kigali Heights"
    assert after["tin"] == "555"  # untouched
    assert after["phone"] == "+250788111111"  # untouched
    assert after["company_name"] == DEFAULT_COMPANY_NAME


def test_patch_can_clear_a_field(client, admin_headers):
    client.patch("/api/v1/settings", json={"notification_email": "quotes@wamugii.rw"}, headers=admin_headers)
    cleared = client.patch(
        "/api/v1/settings", json={"notification_email": None}, headers=admin_headers
    ).json()
    assert cleared["notification_email"] is None


def test_invalid_email_is_rejected(client, admin_headers):
    resp = client.patch("/api/v1/settings", json={"notification_email": "not-an-email"}, headers=admin_headers)
    assert resp.status_code == 422


# --- public endpoint --------------------------------------------------------


def test_public_settings_excludes_tin_and_notification_email(client, admin_headers):
    """The TIN belongs on an invoice, not on an open endpoint."""
    client.patch(
        "/api/v1/settings",
        json={
            "tin": "102938475",
            "notification_email": "quotes@wamugii.rw",
            "phone": "+250788000000",
            "email": "hello@wamugii.rw",
            "website": "https://wamugii.rw",
            "address": "KG 11 Ave",
        },
        headers=admin_headers,
    )

    resp = client.get("/api/v1/settings/public")  # no auth
    assert resp.status_code == 200
    body = resp.json()

    assert "tin" not in body
    assert "notification_email" not in body
    # ...and the safe fields are all there.
    assert body["company_name"] == DEFAULT_COMPANY_NAME
    assert body["slogan"] == DEFAULT_SLOGAN
    assert body["phone"] == "+250788000000"
    assert body["email"] == "hello@wamugii.rw"
    assert body["website"] == "https://wamugii.rw"
    assert body["address"] == "KG 11 Ave"
    # The whole serialized payload must not contain the TIN anywhere.
    assert "102938475" not in resp.text
    assert "quotes@wamugii.rw" not in resp.text


# --- quote notification routing ---------------------------------------------


def _submit_quote(client):
    return client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Routing Tester",
            "email": "lead@example.com",
            "phone": "0700000000",
            "project_title": "Routing test",
            "project_description": "checking where the email goes",
        },
    )


def test_quote_email_goes_to_configured_address_only(
    client, admin_headers, staff_headers, sent_emails
):
    client.patch(
        "/api/v1/settings", json={"notification_email": "quotes@wamugii.rw"}, headers=admin_headers
    )
    sent_emails.clear()

    assert _submit_quote(client).status_code == 201

    assert [e["to_email"] for e in sent_emails] == ["quotes@wamugii.rw"]
    assert sent_emails[0]["subject"] == "New Quote Request — Routing test"


def test_quote_email_fans_out_when_unconfigured(client, admin_headers, staff_headers, sent_emails):
    """Null notification_email preserves the original behaviour exactly."""
    settings_row = client.get("/api/v1/settings", headers=admin_headers).json()
    assert settings_row["notification_email"] is None
    sent_emails.clear()

    assert _submit_quote(client).status_code == 201

    recipients = sorted(e["to_email"] for e in sent_emails)
    assert recipients == ["admin@example.com", "staff@example.com"]


def test_in_app_notification_still_fans_out_to_all_staff(
    client, admin_headers, staff_headers, sent_emails
):
    """
    Routing the email to one inbox must not hide the quote from staff inside
    the app — everyone who can act on it still gets the bell notification.
    """
    client.patch(
        "/api/v1/settings", json={"notification_email": "quotes@wamugii.rw"}, headers=admin_headers
    )
    _submit_quote(client)

    for headers in (admin_headers, staff_headers):
        types = [n["type"] for n in client.get("/api/v1/notifications", headers=headers).json()]
        assert "QUOTE_SUBMITTED" in types


# --- company block on invoices ----------------------------------------------


def test_invoice_read_includes_company_block_with_tin(client, admin_headers):
    client.patch(
        "/api/v1/settings",
        json={
            "tin": "102938475",
            "address": "KG 11 Ave, Kigali",
            "phone": "+250788000000",
            "email": "hello@wamugii.rw",
        },
        headers=admin_headers,
    )
    c = _create_client("settings_invoice@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "1000.00", "tax_rate": "18", "status": "SENT"},
        headers=admin_headers,
    ).json()

    assert invoice["company"]["tin"] == "102938475"
    assert invoice["company"]["company_name"] == DEFAULT_COMPANY_NAME
    assert invoice["company"]["address"] == "KG 11 Ave, Kigali"
    assert invoice["company"]["phone"] == "+250788000000"

    fetched = client.get(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers).json()
    assert fetched["company"]["tin"] == "102938475"


def test_invoice_company_block_has_null_tin_when_unset(client, admin_headers):
    """No TIN configured yet: the field is null so the frontend omits the line."""
    c = _create_client("settings_notin@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()
    assert invoice["company"]["tin"] is None
    assert invoice["company"]["company_name"] == DEFAULT_COMPANY_NAME


def test_client_invoice_view_includes_company_block(client, admin_headers):
    client.patch("/api/v1/settings", json={"tin": "102938475"}, headers=admin_headers)
    c = _create_client("settings_clientinv@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "1000.00", "tax_rate": "18", "status": "SENT"},
        headers=admin_headers,
    ).json()

    body = client.get(f"/api/v1/client/invoices/{invoice['id']}", headers=_auth(c)).json()
    assert body["company"]["tin"] == "102938475"
    assert body["company"]["company_name"] == DEFAULT_COMPANY_NAME
    # Staff-only fields still absent from the client payload.
    assert "notes" not in body
    assert "notification_email" not in body["company"]


def test_updated_settings_apply_to_existing_invoices(client, admin_headers):
    """
    The block is rendered at read time, so entering the TIN later fixes every
    invoice rather than only new ones.
    """
    c = _create_client("settings_retro@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()
    assert invoice["company"]["tin"] is None

    client.patch("/api/v1/settings", json={"tin": "999888777"}, headers=admin_headers)

    refetched = client.get(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers).json()
    assert refetched["company"]["tin"] == "999888777"
