from datetime import date, timedelta

import pytest

from app.core.security import create_access_token
from app.crud import domain as domain_crud
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


def _make_client(email: str, full_name: str = "Domain Client"):
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


def _make_domain(client, headers, client_id: int, **overrides):
    payload = {
        "client_id": client_id,
        "domain_name": "clientsite.rw",
        "registration_fee": "15000.00",
        "service_fee": "5000.00",
    }
    payload.update(overrides)
    return client.post("/api/v1/domains", json=payload, headers=headers)


def _make_hosting(client, admin_headers, client_id: int):
    plan = client.post(
        "/api/v1/hosting/plans",
        json={"name": "Dom Plan", "features": "1 site", "monthly_price": "10000.00",
              "yearly_price": "100000.00", "display_order": 1, "is_active": True},
        headers=admin_headers,
    ).json()
    return client.post(
        "/api/v1/hosting/accounts",
        json={"client_id": client_id, "plan_id": plan["id"]},
        headers=admin_headers,
    ).json()


# --- creation ---------------------------------------------------------------


def test_admin_creates_a_standalone_domain(client, admin_headers, sent_emails):
    """No hosting link — a domain can exist on its own."""
    c = _make_client("dom_standalone@example.com")
    resp = _make_domain(client, admin_headers, c.id)
    assert resp.status_code == 201
    body = resp.json()
    assert body["hosting_account_id"] is None
    assert body["status"] == "PENDING"
    assert body["registrar"] == "Namecheap"  # default
    assert body["registration_fee"] == "15000.00"
    assert body["service_fee"] == "5000.00"
    # Derived, so it can't drift from the two parts.
    assert body["total_fee"] == "20000.00"


def test_service_fee_may_be_zero_or_absent(client, admin_headers, sent_emails):
    c = _make_client("dom_nofee@example.com")
    zero = _make_domain(client, admin_headers, c.id, service_fee="0").json()
    assert zero["total_fee"] == "15000.00"

    absent = _make_domain(client, admin_headers, c.id, domain_name="two.rw", service_fee=None).json()
    assert absent["service_fee"] is None
    assert absent["total_fee"] == "15000.00"


def test_staff_can_create_a_domain(client, staff_headers, sent_emails):
    c = _make_client("dom_staff@example.com")
    assert _make_domain(client, staff_headers, c.id).status_code == 201


def test_client_cannot_create_a_domain(client, client_headers, sent_emails):
    c = _make_client("dom_denied@example.com")
    assert _make_domain(client, client_headers, c.id).status_code == 403


def test_domain_requires_an_active_client_role_user(client, admin_headers, staff_headers, sent_emails):
    db = TestingSessionLocal()
    try:
        staff = user_crud.create(
            db,
            UserCreate(full_name="S", email="dom_staffrole@example.com", password="password123"),
            role=Role.STAFF,
        )
    finally:
        db.close()
    assert _make_domain(client, admin_headers, staff.id).status_code == 422
    assert _make_domain(client, admin_headers, 999999).status_code == 422


def test_hosting_link_must_belong_to_the_same_client(client, admin_headers, sent_emails):
    owner = _make_client("dom_owner@example.com")
    other = _make_client("dom_other@example.com")
    account = _make_hosting(client, admin_headers, owner.id)

    mismatch = _make_domain(
        client, admin_headers, other.id, hosting_account_id=account["id"]
    )
    assert mismatch.status_code == 422
    assert "different client" in mismatch.json()["detail"]

    ok = _make_domain(client, admin_headers, owner.id, hosting_account_id=account["id"])
    assert ok.status_code == 201
    assert ok.json()["hosting_account_id"] == account["id"]


def test_expired_cannot_be_set_directly(client, admin_headers, sent_emails):
    c = _make_client("dom_expired@example.com")
    assert _make_domain(client, admin_headers, c.id, status="EXPIRED").status_code == 422


# --- notifications ----------------------------------------------------------


def test_creation_notifies_and_emails_the_client(client, admin_headers, sent_emails):
    c = _make_client("dom_notify@example.com")
    _make_domain(client, admin_headers, c.id, domain_name="notify.rw")

    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "DOMAIN_REGISTERED" in types
    assert [e["to_email"] for e in sent_emails] == ["dom_notify@example.com"]
    assert sent_emails[0]["subject"] == "Domain registration started — notify.rw"
    assert "RWF 20000.00" in sent_emails[0]["html"]


def test_status_change_to_active_notifies_with_nameservers(client, admin_headers, sent_emails):
    c = _make_client("dom_active@example.com")
    domain = _make_domain(client, admin_headers, c.id, domain_name="live.rw").json()
    sent_emails.clear()

    resp = client.patch(
        f"/api/v1/domains/{domain['id']}",
        json={"status": "ACTIVE", "nameservers": "dns1.namecheaphosting.com"},
        headers=admin_headers,
    )
    assert resp.status_code == 200

    notes = client.get("/api/v1/notifications", headers=_auth(c)).json()
    changed = [n for n in notes if n["type"] == "DOMAIN_STATUS_CHANGED"]
    assert len(changed) == 1
    assert "dns1.namecheaphosting.com" in changed[0]["message"]

    assert [e["to_email"] for e in sent_emails] == ["dom_active@example.com"]
    assert sent_emails[0]["subject"] == "live.rw is now active"
    assert "dns1.namecheaphosting.com" in sent_emails[0]["html"]


@pytest.mark.parametrize("status", ["CANCELLED"])
def test_cancellation_notifies_the_client(client, admin_headers, sent_emails, status):
    c = _make_client(f"dom_{status.lower()}@example.com")
    domain = _make_domain(client, admin_headers, c.id).json()
    sent_emails.clear()

    client.patch(f"/api/v1/domains/{domain['id']}", json={"status": status}, headers=admin_headers)
    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "DOMAIN_STATUS_CHANGED" in types
    assert len(sent_emails) == 1


def test_non_status_edit_does_not_notify(client, admin_headers, sent_emails):
    c = _make_client("dom_quiet@example.com")
    domain = _make_domain(client, admin_headers, c.id).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/domains/{domain['id']}", json={"notes": "registered via reseller"},
        headers=admin_headers,
    )
    assert sent_emails == []


def test_resaving_the_same_status_does_not_renotify(client, admin_headers, sent_emails):
    c = _make_client("dom_resave@example.com")
    domain = _make_domain(client, admin_headers, c.id).json()
    client.patch(f"/api/v1/domains/{domain['id']}", json={"status": "ACTIVE"}, headers=admin_headers)
    sent_emails.clear()
    client.patch(f"/api/v1/domains/{domain['id']}", json={"status": "ACTIVE"}, headers=admin_headers)
    assert sent_emails == []


# --- client scoping & notes leakage -----------------------------------------


def test_client_sees_only_their_own_domains(client, admin_headers, sent_emails):
    c1 = _make_client("dom_mine@example.com")
    c2 = _make_client("dom_theirs@example.com")
    mine = _make_domain(client, admin_headers, c1.id, domain_name="mine.rw").json()
    _make_domain(client, admin_headers, c2.id, domain_name="theirs.rw")

    listed = client.get("/api/v1/client/domains", headers=_auth(c1)).json()
    assert [d["id"] for d in listed] == [mine["id"]]
    assert [d["domain_name"] for d in listed] == ["mine.rw"]


def test_cross_client_domain_detail_returns_404(client, admin_headers, sent_emails):
    c1 = _make_client("dom_a@example.com")
    c2 = _make_client("dom_b@example.com")
    theirs = _make_domain(client, admin_headers, c1.id).json()
    assert client.get(f"/api/v1/client/domains/{theirs['id']}", headers=_auth(c2)).status_code == 404


def test_internal_notes_never_reach_the_client(client, admin_headers, sent_emails):
    """The key leak check for this module."""
    c = _make_client("dom_notes@example.com")
    domain = _make_domain(client, admin_headers, c.id, domain_name="secret.rw").json()
    SECRET = "bought via reseller acct #4471 — margin 8k — INTERNAL"

    client.patch(
        f"/api/v1/domains/{domain['id']}",
        json={"status": "ACTIVE", "nameservers": "dns1.example.com", "notes": SECRET},
        headers=admin_headers,
    )

    # Staff see it...
    staff_view = client.get(f"/api/v1/domains/{domain['id']}", headers=admin_headers).json()
    assert staff_view["notes"] == SECRET

    # ...the client never does, in the list or the detail.
    listed = client.get("/api/v1/client/domains", headers=_auth(c))
    assert "notes" not in listed.json()[0]
    assert SECRET not in listed.text

    detail = client.get(f"/api/v1/client/domains/{domain['id']}", headers=_auth(c))
    assert "notes" not in detail.json()
    assert SECRET not in detail.text
    # But the nameservers and what they paid are there.
    assert detail.json()["nameservers"] == "dns1.example.com"
    assert detail.json()["total_fee"] == "20000.00"


def test_soft_delete_hides_the_domain_everywhere(client, admin_headers, sent_emails):
    c = _make_client("dom_del@example.com")
    domain = _make_domain(client, admin_headers, c.id).json()

    deleted = client.delete(f"/api/v1/domains/{domain['id']}", headers=admin_headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    assert domain["id"] not in [
        d["id"] for d in client.get("/api/v1/domains", headers=admin_headers).json()
    ]
    assert client.get("/api/v1/client/domains", headers=_auth(c)).json() == []
    assert client.get(f"/api/v1/client/domains/{domain['id']}", headers=_auth(c)).status_code == 404


def test_staff_cannot_delete_a_domain(client, admin_headers, staff_headers, sent_emails):
    c = _make_client("dom_staffdel@example.com")
    domain = _make_domain(client, admin_headers, c.id).json()
    assert client.delete(
        f"/api/v1/domains/{domain['id']}", headers=staff_headers
    ).status_code == 403


# --- filters & helpers ------------------------------------------------------


def test_domain_filters(client, admin_headers, sent_emails):
    c1 = _make_client("dom_f1@example.com")
    c2 = _make_client("dom_f2@example.com")
    a = _make_domain(client, admin_headers, c1.id, domain_name="alpha.rw").json()
    _make_domain(client, admin_headers, c2.id, domain_name="beta.rw")
    client.patch(f"/api/v1/domains/{a['id']}", json={"status": "ACTIVE"}, headers=admin_headers)

    def ids(**params):
        return [
            d["id"]
            for d in client.get("/api/v1/domains", params=params, headers=admin_headers).json()
        ]

    assert ids(status="ACTIVE") == [a["id"]]
    assert ids(client_id=c1.id) == [a["id"]]
    assert ids(search="alpha") == [a["id"]]


def test_expiring_soon_finds_only_active_domains_in_window(client, admin_headers, sent_emails):
    c = _make_client("dom_expiring@example.com")
    soon = (date.today() + timedelta(days=10)).isoformat()
    far = (date.today() + timedelta(days=200)).isoformat()

    a = _make_domain(client, admin_headers, c.id, domain_name="soon.rw", expires_at=soon).json()
    b = _make_domain(client, admin_headers, c.id, domain_name="far.rw", expires_at=far).json()
    for d in (a, b):
        client.patch(f"/api/v1/domains/{d['id']}", json={"status": "ACTIVE"}, headers=admin_headers)

    db = TestingSessionLocal()
    try:
        found = domain_crud.get_domains_expiring_soon(db, days=30)
    finally:
        db.close()
    assert [x.id for x in found] == [a["id"]]


def test_invoice_can_be_linked_back(client, admin_headers, sent_emails):
    """Billing runs through the existing invoice system, not a new one."""
    c = _make_client("dom_invoice@example.com")
    domain = _make_domain(client, admin_headers, c.id).json()

    invoice = client.post(
        "/api/v1/invoices",
        json={
            "client_id": c.id, "subtotal": "0", "status": "SENT",
            "items": [{"description": "Domain clientsite.rw (registration + service)",
                       "quantity": "1", "unit_price": domain["total_fee"]}],
        },
        headers=admin_headers,
    ).json()
    assert invoice["total"] == "20000.00"

    linked = client.patch(
        f"/api/v1/domains/{domain['id']}", json={"invoice_id": invoice["id"]}, headers=admin_headers
    ).json()
    assert linked["invoice_id"] == invoice["id"]
