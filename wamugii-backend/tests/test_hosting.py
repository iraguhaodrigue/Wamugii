from datetime import date

import pytest

from app.core.security import create_access_token
from app.crud import hosting as hosting_crud
from app.models.hosting import BillingCycle
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


def _create_client_user(email: str, full_name: str = "Hosting Client"):
    db = TestingSessionLocal()
    try:
        return user_crud_create(db, email, full_name)
    finally:
        db.close()


def user_crud_create(db, email, full_name):
    from app.crud import user as user_crud

    return user_crud.create(
        db,
        UserCreate(full_name=full_name, email=email, password="password123"),
        role=Role.CLIENT,
    )


def _auth(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _make_plan(client, admin_headers, name="Test Plan", **overrides) -> dict:
    payload = {
        "name": name,
        "features": "1 website, SSL",
        "monthly_price": "10000.00",
        "yearly_price": "100000.00",
        "display_order": 1,
    }
    payload.update(overrides)
    resp = client.post("/api/v1/hosting/plans", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _make_account(client, headers, client_id: int, plan_id: int, **overrides) -> dict:
    payload = {"client_id": client_id, "plan_id": plan_id}
    payload.update(overrides)
    return client.post("/api/v1/hosting/accounts", json=payload, headers=headers)


# --- plans: public read, admin write ----------------------------------------


def test_anyone_can_list_hosting_plans(client, admin_headers):
    _make_plan(client, admin_headers, "Public Plan")
    resp = client.get("/api/v1/hosting/plans")  # no auth
    assert resp.status_code == 200
    assert [p["name"] for p in resp.json()] == ["Public Plan"]


def test_plans_are_ordered_by_display_order(client, admin_headers):
    _make_plan(client, admin_headers, "Third", display_order=3)
    _make_plan(client, admin_headers, "First", display_order=1)
    _make_plan(client, admin_headers, "Second", display_order=2)
    names = [p["name"] for p in client.get("/api/v1/hosting/plans").json()]
    assert names == ["First", "Second", "Third"]


def test_plan_prices_are_decimal_strings(client, admin_headers):
    plan = _make_plan(client, admin_headers, monthly_price="20000.00", yearly_price="200000.00")
    assert plan["monthly_price"] == "20000.00"
    assert plan["yearly_price"] == "200000.00"


def test_admin_can_update_and_deactivate_a_plan(client, admin_headers):
    plan = _make_plan(client, admin_headers)

    updated = client.patch(
        f"/api/v1/hosting/plans/{plan['id']}",
        json={"monthly_price": "12500.00", "features": "2 websites, SSL"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["monthly_price"] == "12500.00"
    assert updated.json()["features"] == "2 websites, SSL"

    gone = client.delete(f"/api/v1/hosting/plans/{plan['id']}", headers=admin_headers)
    assert gone.status_code == 200
    assert gone.json()["is_active"] is False
    # Deactivated plans drop out of the public list.
    assert plan["id"] not in [p["id"] for p in client.get("/api/v1/hosting/plans").json()]


def test_client_cannot_manage_plans(client, client_headers):
    assert client.post(
        "/api/v1/hosting/plans", json={"name": "Nope"}, headers=client_headers
    ).status_code == 403
    assert client.patch(
        "/api/v1/hosting/plans/1", json={"name": "Nope"}, headers=client_headers
    ).status_code == 403
    assert client.delete("/api/v1/hosting/plans/1", headers=client_headers).status_code == 403


def test_staff_cannot_manage_plans(client, staff_headers):
    """Plan pricing is an ADMIN decision."""
    assert client.post(
        "/api/v1/hosting/plans", json={"name": "Nope"}, headers=staff_headers
    ).status_code == 403


def test_unknown_plan_returns_404(client):
    assert client.get("/api/v1/hosting/plans/999999").status_code == 404


# --- accounts: creation & validation ----------------------------------------


def test_admin_can_create_a_hosting_account(client, admin_headers, sent_emails):
    c = _create_client_user("host_create@example.com")
    plan = _make_plan(client, admin_headers)

    resp = _make_account(
        client,
        admin_headers,
        c.id,
        plan["id"],
        domain="clientsite.rw",
        billing_cycle="MONTHLY",
        start_date="2026-01-15",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PENDING"
    assert body["domain"] == "clientsite.rw"
    # Derived server-side from start_date + cycle.
    assert body["next_billing_date"] == "2026-02-15"


def test_staff_can_create_a_hosting_account(client, admin_headers, staff_headers, sent_emails):
    c = _create_client_user("host_staff@example.com")
    plan = _make_plan(client, admin_headers)
    assert _make_account(client, staff_headers, c.id, plan["id"]).status_code == 201


def test_client_cannot_create_a_hosting_account(client, admin_headers, client_headers):
    c = _create_client_user("host_denied@example.com")
    plan = _make_plan(client, admin_headers)
    resp = _make_account(client, client_headers, c.id, plan["id"])
    assert resp.status_code == 403


def test_account_requires_an_active_client_role_user(client, admin_headers, sent_emails):
    plan = _make_plan(client, admin_headers)
    # A staff user is not a valid hosting client.
    from app.crud import user as user_crud

    db = TestingSessionLocal()
    try:
        staff = user_crud.create(
            db,
            UserCreate(full_name="Staffer", email="host_staffrole@example.com", password="password123"),
            role=Role.STAFF,
        )
    finally:
        db.close()

    assert _make_account(client, admin_headers, staff.id, plan["id"]).status_code == 422
    assert _make_account(client, admin_headers, 999999, plan["id"]).status_code == 422


def test_account_requires_an_active_plan(client, admin_headers, sent_emails):
    c = _create_client_user("host_badplan@example.com")
    plan = _make_plan(client, admin_headers)
    client.delete(f"/api/v1/hosting/plans/{plan['id']}", headers=admin_headers)

    assert _make_account(client, admin_headers, c.id, plan["id"]).status_code == 422
    assert _make_account(client, admin_headers, c.id, 999999).status_code == 422


def test_yearly_cycle_advances_a_year(client, admin_headers, sent_emails):
    c = _create_client_user("host_yearly@example.com")
    plan = _make_plan(client, admin_headers)
    body = _make_account(
        client, admin_headers, c.id, plan["id"], billing_cycle="YEARLY", start_date="2026-03-01"
    ).json()
    assert body["next_billing_date"] == "2027-03-01"


def test_derived_status_cannot_be_set_directly(client, admin_headers, sent_emails):
    """EXPIRED describes a date passing, not an admin decision."""
    c = _create_client_user("host_expired@example.com")
    plan = _make_plan(client, admin_headers)
    assert _make_account(client, admin_headers, c.id, plan["id"], status="EXPIRED").status_code == 422


# --- notifications ----------------------------------------------------------


def test_account_creation_notifies_the_client(client, admin_headers, sent_emails):
    c = _create_client_user("host_notify@example.com")
    plan = _make_plan(client, admin_headers)
    _make_account(client, admin_headers, c.id, plan["id"], domain="notify.rw")

    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "HOSTING_ACCOUNT_CREATED" in types
    assert [e["to_email"] for e in sent_emails] == ["host_notify@example.com"]
    assert sent_emails[0]["subject"] == "Your WAMUGII hosting account has been created"


def test_status_change_to_active_notifies_the_client(client, admin_headers, sent_emails):
    c = _create_client_user("host_active@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"], domain="live.rw").json()
    sent_emails.clear()

    resp = client.patch(
        f"/api/v1/hosting/accounts/{account['id']}",
        json={"status": "ACTIVE", "nameservers": "ns1.wamugii.rw, ns2.wamugii.rw"},
        headers=admin_headers,
    )
    assert resp.status_code == 200

    notes = client.get("/api/v1/notifications", headers=_auth(c)).json()
    status_notes = [n for n in notes if n["type"] == "HOSTING_STATUS_CHANGED"]
    assert len(status_notes) == 1
    assert "ns1.wamugii.rw" in status_notes[0]["message"]

    assert [e["to_email"] for e in sent_emails] == ["host_active@example.com"]
    assert sent_emails[0]["subject"] == "Your hosting for live.rw is now active"
    assert "ns1.wamugii.rw" in sent_emails[0]["html"]


def test_status_change_to_suspended_notifies_the_client(client, admin_headers, sent_emails):
    c = _create_client_user("host_susp@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"]).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/hosting/accounts/{account['id']}",
        json={"status": "SUSPENDED"},
        headers=admin_headers,
    )
    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(c)).json()]
    assert "HOSTING_STATUS_CHANGED" in types
    assert len(sent_emails) == 1


def test_non_status_edit_does_not_notify(client, admin_headers, sent_emails):
    c = _create_client_user("host_quiet@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"]).json()
    sent_emails.clear()

    client.patch(
        f"/api/v1/hosting/accounts/{account['id']}",
        json={"server_notes": "droplet-3, plesk user wam3"},
        headers=admin_headers,
    )
    assert sent_emails == []


def test_resaving_the_same_status_does_not_renotify(client, admin_headers, sent_emails):
    c = _create_client_user("host_resave@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"]).json()

    client.patch(
        f"/api/v1/hosting/accounts/{account['id']}", json={"status": "ACTIVE"}, headers=admin_headers
    )
    sent_emails.clear()
    client.patch(
        f"/api/v1/hosting/accounts/{account['id']}", json={"status": "ACTIVE"}, headers=admin_headers
    )
    assert sent_emails == []


# --- client scoping & server_notes leakage ----------------------------------


def test_client_sees_only_their_own_hosting(client, admin_headers, sent_emails):
    c1 = _create_client_user("host_mine@example.com")
    c2 = _create_client_user("host_theirs@example.com")
    plan = _make_plan(client, admin_headers)
    mine = _make_account(client, admin_headers, c1.id, plan["id"], domain="mine.rw").json()
    _make_account(client, admin_headers, c2.id, plan["id"], domain="theirs.rw")

    listed = client.get("/api/v1/client/hosting", headers=_auth(c1)).json()
    assert [a["id"] for a in listed] == [mine["id"]]
    assert [a["domain"] for a in listed] == ["mine.rw"]


def test_cross_client_hosting_detail_returns_404(client, admin_headers, sent_emails):
    c1 = _create_client_user("host_a@example.com")
    c2 = _create_client_user("host_b@example.com")
    plan = _make_plan(client, admin_headers)
    theirs = _make_account(client, admin_headers, c1.id, plan["id"]).json()

    resp = client.get(f"/api/v1/client/hosting/{theirs['id']}", headers=_auth(c2))
    assert resp.status_code == 404


def test_server_notes_never_reach_the_client(client, admin_headers, sent_emails):
    """The single most important leak check in this module."""
    c = _create_client_user("host_notes@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"], domain="secret.rw").json()

    secret = "droplet-7 / plesk user wam7 / root creds in vault"
    client.patch(
        f"/api/v1/hosting/accounts/{account['id']}",
        json={
            "status": "ACTIVE",
            "nameservers": "ns1.wamugii.rw",
            "server_notes": secret,
        },
        headers=admin_headers,
    )

    # Staff see it...
    staff_view = client.get(f"/api/v1/hosting/accounts/{account['id']}", headers=admin_headers).json()
    assert staff_view["server_notes"] == secret

    # ...the client never does, in the list or the detail.
    listed = client.get("/api/v1/client/hosting", headers=_auth(c))
    assert "server_notes" not in listed.json()[0]
    assert secret not in listed.text

    detail = client.get(f"/api/v1/client/hosting/{account['id']}", headers=_auth(c))
    assert "server_notes" not in detail.json()
    assert secret not in detail.text
    # But the nameservers they need are there.
    assert detail.json()["nameservers"] == "ns1.wamugii.rw"


def test_client_hosting_detail_includes_plan_features(client, admin_headers, sent_emails):
    c = _create_client_user("host_features@example.com")
    plan = _make_plan(client, admin_headers, features="3 websites, SSL, 50GB SSD")
    account = _make_account(client, admin_headers, c.id, plan["id"]).json()

    detail = client.get(f"/api/v1/client/hosting/{account['id']}", headers=_auth(c)).json()
    assert detail["plan"]["features"] == "3 websites, SSL, 50GB SSD"
    assert detail["plan"]["monthly_price"] == "10000.00"


def test_soft_deleted_account_hides_from_both_lists(client, admin_headers, sent_emails):
    c = _create_client_user("host_del@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"]).json()

    deleted = client.delete(f"/api/v1/hosting/accounts/{account['id']}", headers=admin_headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False

    assert account["id"] not in [
        a["id"] for a in client.get("/api/v1/hosting/accounts", headers=admin_headers).json()
    ]
    assert client.get("/api/v1/client/hosting", headers=_auth(c)).json() == []
    assert client.get(f"/api/v1/client/hosting/{account['id']}", headers=_auth(c)).status_code == 404


def test_staff_cannot_delete_an_account(client, admin_headers, staff_headers, sent_emails):
    c = _create_client_user("host_staffdel@example.com")
    plan = _make_plan(client, admin_headers)
    account = _make_account(client, admin_headers, c.id, plan["id"]).json()
    assert client.delete(
        f"/api/v1/hosting/accounts/{account['id']}", headers=staff_headers
    ).status_code == 403


# --- filters ----------------------------------------------------------------


def test_account_filters(client, admin_headers, sent_emails):
    c1 = _create_client_user("host_f1@example.com")
    c2 = _create_client_user("host_f2@example.com")
    plan_a = _make_plan(client, admin_headers, "Plan A", display_order=1)
    plan_b = _make_plan(client, admin_headers, "Plan B", display_order=2)

    a = _make_account(client, admin_headers, c1.id, plan_a["id"], domain="alpha.rw").json()
    _make_account(client, admin_headers, c2.id, plan_b["id"], domain="beta.rw")
    client.patch(
        f"/api/v1/hosting/accounts/{a['id']}", json={"status": "ACTIVE"}, headers=admin_headers
    )

    by_status = client.get(
        "/api/v1/hosting/accounts", params={"status": "ACTIVE"}, headers=admin_headers
    ).json()
    assert [x["id"] for x in by_status] == [a["id"]]

    by_plan = client.get(
        "/api/v1/hosting/accounts", params={"plan_id": plan_a["id"]}, headers=admin_headers
    ).json()
    assert [x["id"] for x in by_plan] == [a["id"]]

    by_client = client.get(
        "/api/v1/hosting/accounts", params={"client_id": c1.id}, headers=admin_headers
    ).json()
    assert [x["id"] for x in by_client] == [a["id"]]

    by_domain = client.get(
        "/api/v1/hosting/accounts", params={"search": "alpha"}, headers=admin_headers
    ).json()
    assert [x["id"] for x in by_domain] == [a["id"]]


# --- dashboard --------------------------------------------------------------


def test_dashboard_hosting_count_is_real(client, admin_headers, sent_emails):
    before = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert before["hosting"] == {"active": 0}

    c = _create_client_user("host_dash@example.com")
    plan = _make_plan(client, admin_headers)
    pending = _make_account(client, admin_headers, c.id, plan["id"]).json()

    # PENDING doesn't count.
    mid = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert mid["hosting"]["active"] == 0

    client.patch(
        f"/api/v1/hosting/accounts/{pending['id']}", json={"status": "ACTIVE"}, headers=admin_headers
    )
    after = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert after["hosting"]["active"] == 1

    # Soft-deleting drops it back out.
    client.delete(f"/api/v1/hosting/accounts/{pending['id']}", headers=admin_headers)
    final = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert final["hosting"]["active"] == 0


def test_dashboard_shape_is_unchanged(client, admin_headers):
    body = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert set(body) == {
        "users", "services", "projects", "quotes", "invoices", "hosting", "store", "support",
        "team",
    }
    assert set(body["hosting"]) == {"active"}


# --- billing-date helper ----------------------------------------------------


@pytest.mark.parametrize(
    "start,cycle,expected",
    [
        (date(2026, 1, 15), BillingCycle.MONTHLY, date(2026, 2, 15)),
        (date(2026, 1, 31), BillingCycle.MONTHLY, date(2026, 2, 28)),  # clamped
        (date(2026, 12, 15), BillingCycle.MONTHLY, date(2027, 1, 15)),  # year rolls
        (date(2026, 3, 1), BillingCycle.YEARLY, date(2027, 3, 1)),
        (date(2028, 2, 29), BillingCycle.YEARLY, date(2029, 2, 28)),  # leap -> non-leap
    ],
)
def test_compute_next_billing_date(start, cycle, expected):
    assert hosting_crud.compute_next_billing_date(start, cycle) == expected


def test_compute_next_billing_date_passes_none_through():
    assert hosting_crud.compute_next_billing_date(None, BillingCycle.MONTHLY) is None


def test_expiring_soon_finds_only_active_accounts_in_window(client, admin_headers, sent_emails):
    from datetime import timedelta

    c = _create_client_user("host_expiring@example.com")
    plan = _make_plan(client, admin_headers)
    soon = (date.today() + timedelta(days=3)).isoformat()
    far = (date.today() + timedelta(days=60)).isoformat()

    a = _make_account(client, admin_headers, c.id, plan["id"], expires_at=soon).json()
    b = _make_account(client, admin_headers, c.id, plan["id"], expires_at=far).json()
    for acc in (a, b):
        client.patch(
            f"/api/v1/hosting/accounts/{acc['id']}", json={"status": "ACTIVE"}, headers=admin_headers
        )

    db = TestingSessionLocal()
    try:
        found = hosting_crud.get_accounts_expiring_soon(db, days=7)
    finally:
        db.close()
    assert [x.id for x in found] == [a["id"]]
