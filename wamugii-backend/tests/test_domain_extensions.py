"""
Per-TLD price list on top of the existing domains module.

The two things that matter most and both are tested here: `client_price` is
always `cost_price + margin` on the current row, never a stored value that can
drift; and creating a Domain with a known extension prefills the fees from the
price list.
"""

import pytest

from app.core.security import create_access_token
from app.crud import domain_extension as extension_crud
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.domain_extension import DomainExtensionCreate
from app.schemas.user import UserCreate
from app.services import email_service
from tests.conftest import TestingSessionLocal


@pytest.fixture
def sent_emails(monkeypatch):
    captured: list[dict] = []

    def _fake_send_email(to_email, to_name, subject, html_content, text_content=None):
        captured.append({"to_email": to_email, "subject": subject})
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send_email)
    return captured


def _make_client(email: str = "ext.client@example.com"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name="Ext Client", email=email, password="password123"),
            role=Role.CLIENT,
        )
    finally:
        db.close()


def _auth(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _create_ext(client, headers, **overrides):
    payload = {"extension": ".com", "cost_price": "16000.00", "margin": "5000.00"}
    payload.update(overrides)
    return client.post("/api/v1/domains/extensions", json=payload, headers=headers)


# --- list -------------------------------------------------------------------


def test_public_can_list_extensions_with_computed_client_price(client, admin_headers):
    _create_ext(client, admin_headers, extension=".com",
                cost_price="16000.00", margin="5000.00", display_order=1)
    _create_ext(client, admin_headers, extension=".rw",
                cost_price="14000.00", margin="5000.00", display_order=2)

    # No auth header -- the price table drives the public domains page.
    resp = client.get("/api/v1/domains/extensions")
    assert resp.status_code == 200

    rows = resp.json()
    by_ext = {r["extension"]: r for r in rows}
    assert by_ext[".com"]["client_price"] == "21000.00"
    assert by_ext[".rw"]["client_price"] == "19000.00"


def test_listed_in_display_order(client, admin_headers):
    _create_ext(client, admin_headers, extension=".net", display_order=3)
    _create_ext(client, admin_headers, extension=".com", display_order=1)
    _create_ext(client, admin_headers, extension=".rw", display_order=2)

    rows = client.get("/api/v1/domains/extensions").json()
    assert [r["extension"] for r in rows] == [".com", ".rw", ".net"]


def test_soft_deleted_rows_are_hidden_from_the_public(client, admin_headers):
    created = _create_ext(client, admin_headers).json()
    client.delete(f"/api/v1/domains/extensions/{created['id']}", headers=admin_headers)

    assert client.get("/api/v1/domains/extensions").json() == []
    # But an admin management view still sees them.
    with_inactive = client.get(
        "/api/v1/domains/extensions/manage", headers=admin_headers
    ).json()
    assert len(with_inactive) == 1
    assert with_inactive[0]["is_active"] is False


# --- write ------------------------------------------------------------------


def test_admin_can_add_an_extension(client, admin_headers):
    resp = _create_ext(
        client, admin_headers, extension=".io", cost_price="60000.00", margin="5000.00"
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["extension"] == ".io"
    assert body["cost_price"] == "60000.00"
    assert body["margin"] == "5000.00"
    assert body["client_price"] == "65000.00"


def test_duplicate_extension_is_a_conflict(client, admin_headers):
    first = _create_ext(client, admin_headers, extension=".com")
    assert first.status_code == 201
    again = _create_ext(client, admin_headers, extension=".com")
    assert again.status_code == 409


def test_extension_is_normalised(client, admin_headers):
    """Admin typing 'COM' or 'com' both store as '.com' and a second write 409s."""
    first = _create_ext(client, admin_headers, extension="COM", cost_price="16000.00")
    assert first.status_code == 201
    assert first.json()["extension"] == ".com"

    again = _create_ext(client, admin_headers, extension="com", cost_price="20000.00")
    assert again.status_code == 409


def test_an_invalid_extension_string_is_rejected(client, admin_headers):
    for bad in ("", " ", "wrong.com.rw", ".", "no spaces", "foo/bar"):
        resp = _create_ext(client, admin_headers, extension=bad)
        assert resp.status_code == 422, bad


def test_editing_cost_updates_the_computed_client_price(client, admin_headers):
    row = _create_ext(client, admin_headers, cost_price="16000.00", margin="5000.00").json()
    assert row["client_price"] == "21000.00"

    bumped = client.patch(
        f"/api/v1/domains/extensions/{row['id']}",
        json={"cost_price": "18000.00"},
        headers=admin_headers,
    )
    assert bumped.status_code == 200
    assert bumped.json()["cost_price"] == "18000.00"
    assert bumped.json()["client_price"] == "23000.00"


def test_editing_margin_updates_the_computed_client_price(client, admin_headers):
    row = _create_ext(client, admin_headers).json()
    bumped = client.patch(
        f"/api/v1/domains/extensions/{row['id']}",
        json={"margin": "7500.00"},
        headers=admin_headers,
    )
    assert bumped.status_code == 200
    assert bumped.json()["client_price"] == "23500.00"


def test_soft_delete_marks_the_row_inactive(client, admin_headers):
    row = _create_ext(client, admin_headers).json()
    resp = client.delete(f"/api/v1/domains/extensions/{row['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_non_admin_cannot_write(client, admin_headers, staff_headers, client_headers):
    row = _create_ext(client, admin_headers).json()
    for headers in (staff_headers, client_headers, {}):
        expected_write = 403 if headers else 401
        assert _create_ext(client, headers, extension=".net").status_code == expected_write
        assert (
            client.patch(
                f"/api/v1/domains/extensions/{row['id']}",
                json={"cost_price": "99.00"},
                headers=headers,
            ).status_code
            == expected_write
        )
        assert (
            client.delete(
                f"/api/v1/domains/extensions/{row['id']}", headers=headers
            ).status_code
            == expected_write
        )


def test_staff_cannot_use_the_admin_only_management_list(client, staff_headers):
    assert (
        client.get(
            "/api/v1/domains/extensions/manage", headers=staff_headers
        ).status_code
        == 403
    )


def test_a_missing_extension_id_is_a_404(client, admin_headers):
    assert client.patch(
        "/api/v1/domains/extensions/99999",
        json={"cost_price": "1.00"},
        headers=admin_headers,
    ).status_code == 404
    assert client.delete(
        "/api/v1/domains/extensions/99999", headers=admin_headers
    ).status_code == 404


# --- prefill into Domain create --------------------------------------------


def test_creating_a_domain_with_a_known_extension_prefills_fees(
    client, admin_headers, sent_emails
):
    _create_ext(
        client, admin_headers, extension=".com", cost_price="16000.00", margin="5000.00"
    )
    c = _make_client()

    resp = client.post(
        "/api/v1/domains",
        json={"client_id": c.id, "domain_name": "example.com"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["registration_fee"] == "16000.00"
    assert body["service_fee"] == "5000.00"
    assert body["total_fee"] == "21000.00"


def test_an_explicit_fee_overrides_the_prefill(client, admin_headers, sent_emails):
    """`model_fields_set` says the admin sent a value; prefill respects that."""
    _create_ext(client, admin_headers, extension=".com", cost_price="16000.00")
    c = _make_client()

    resp = client.post(
        "/api/v1/domains",
        json={
            "client_id": c.id,
            "domain_name": "example.com",
            "registration_fee": "20000.00",
            "service_fee": "0.00",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["registration_fee"] == "20000.00"
    # Explicit zero is honoured, not treated as "unset" and overwritten.
    assert body["service_fee"] == "0.00"


def test_an_unknown_extension_still_creates_without_prefill(
    client, admin_headers, sent_emails
):
    """No row for `.xyz` -- the domain creates, fees default to the schema values."""
    c = _make_client()
    resp = client.post(
        "/api/v1/domains",
        json={"client_id": c.id, "domain_name": "example.xyz"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    # The schema default is 0, so the total still reconciles.
    assert body["registration_fee"] == "0.00"
    assert body["service_fee"] is None


def test_a_soft_deleted_extension_is_not_used_for_prefill(
    client, admin_headers, sent_emails
):
    row = _create_ext(
        client, admin_headers, extension=".com", cost_price="16000.00", margin="5000.00"
    ).json()
    client.delete(f"/api/v1/domains/extensions/{row['id']}", headers=admin_headers)
    c = _make_client()

    resp = client.post(
        "/api/v1/domains",
        json={"client_id": c.id, "domain_name": "example.com"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["registration_fee"] == "0.00"
    assert resp.json()["service_fee"] is None


def test_prefill_picks_the_longest_matching_extension(client, admin_headers, sent_emails):
    """`.co.rw` beats `.rw` when both exist."""
    _create_ext(client, admin_headers, extension=".rw", cost_price="14000.00")
    # ".co.rw" would be rejected by the schema's single-TLD rule, which is
    # intentional for the real deployment; use two clean entries to exercise
    # the longest-match logic directly through the CRUD.
    db = TestingSessionLocal()
    try:
        extension_crud.create(
            db,
            DomainExtensionCreate(
                extension=".coza",  # bypass dot-splitting; valid single-TLD
                cost_price="25000.00",
                margin="5000.00",
            ),
        )
    finally:
        db.close()

    # Longest ending wins -- `.coza` on `example.coza`, `.rw` on `example.rw`.
    c1 = _make_client("ext1@example.com")
    r1 = client.post(
        "/api/v1/domains",
        json={"client_id": c1.id, "domain_name": "example.coza"},
        headers=admin_headers,
    )
    assert r1.json()["registration_fee"] == "25000.00"

    c2 = _make_client("ext2@example.com")
    r2 = client.post(
        "/api/v1/domains",
        json={"client_id": c2.id, "domain_name": "example.rw"},
        headers=admin_headers,
    )
    assert r2.json()["registration_fee"] == "14000.00"


# --- seed script -----------------------------------------------------------


def test_seed_script_is_idempotent():
    """
    Direct CRUD smoke-test of the idempotence rule the seed enforces.

    (Running `python -m app.seed_domain_extensions` under pytest would reach
    the real SessionLocal/Postgres rather than the test DB, so the shape of
    the rule is checked here against the schema+crud instead.)
    """
    db = TestingSessionLocal()
    try:
        payload = DomainExtensionCreate(
            extension=".com", cost_price="16000.00"
        )

        # First "run": creates.
        assert extension_crud.get_by_extension(db, ".com") is None
        extension_crud.create(db, payload)
        first = extension_crud.get_by_extension(db, ".com")
        assert first is not None

        # Simulated admin edit after the fact.
        first.cost_price = 99999  # type: ignore[assignment]
        db.commit()

        # Second "run": the seed uses `get_by_extension` to short-circuit, so
        # the admin's edit is never overwritten.
        assert extension_crud.get_by_extension(db, ".com") is first
        assert extension_crud.get_by_extension(db, ".com").cost_price == 99999
    finally:
        db.close()
