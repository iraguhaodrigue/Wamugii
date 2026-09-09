import pytest

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.notification import NotificationType
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


def _create_client(email: str, full_name: str = "Notify Client"):
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


def _notifications_for(client, headers, **params) -> list[dict]:
    resp = client.get("/api/v1/notifications", headers=headers, params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


# --- system events create notifications for the right recipient -------------


def test_project_creation_notifies_the_client(client, admin_headers):
    c = _create_client("notify_projcreate@example.com")
    project = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Notified Project", "description": "d"},
        headers=admin_headers,
    ).json()

    items = _notifications_for(client, _auth(c))
    assert len(items) == 1
    assert items[0]["type"] == NotificationType.PROJECT_CREATED.value
    assert items[0]["related_type"] == "project"
    assert items[0]["related_id"] == project["id"]
    assert items[0]["is_read"] is False


def test_project_status_change_notifies_the_client(client, admin_headers):
    c = _create_client("notify_projstatus@example.com")
    project = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Status Project", "description": "d"},
        headers=admin_headers,
    ).json()

    client.patch(
        f"/api/v1/projects/{project['id']}", json={"status": "IN_PROGRESS"}, headers=admin_headers
    )

    types = [n["type"] for n in _notifications_for(client, _auth(c))]
    assert NotificationType.PROJECT_STATUS_CHANGED.value in types


def test_non_status_project_edit_does_not_notify(client, admin_headers):
    """A notes/title edit isn't an event — only a real transition is."""
    c = _create_client("notify_noedit@example.com")
    project = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Quiet Project", "description": "d"},
        headers=admin_headers,
    ).json()

    client.patch(f"/api/v1/projects/{project['id']}", json={"title": "Renamed"}, headers=admin_headers)

    types = [n["type"] for n in _notifications_for(client, _auth(c))]
    assert types == [NotificationType.PROJECT_CREATED.value]


def test_quote_submission_notifies_staff_and_admin(client, admin_headers, staff_headers):
    resp = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Walk-in",
            "email": "walkin@example.com",
            "phone": "0700000000",
            "project_title": "New shop site",
            "project_description": "A site for my shop",
        },
    )
    assert resp.status_code == 201

    for headers in (admin_headers, staff_headers):
        types = [n["type"] for n in _notifications_for(client, headers)]
        assert NotificationType.QUOTE_SUBMITTED.value in types


def test_quote_status_change_notifies_matching_client_account(client, admin_headers):
    c = _create_client("notify_quote@example.com")
    quote = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Notify Client",
            "email": "notify_quote@example.com",
            "phone": "0700000000",
            "project_title": "Quote for a site",
            "project_description": "Please quote this",
        },
    ).json()

    client.patch(
        f"/api/v1/quote-requests/{quote['id']}", json={"status": "REVIEWING"}, headers=admin_headers
    )

    items = _notifications_for(client, _auth(c))
    assert [n["type"] for n in items] == [NotificationType.QUOTE_STATUS_CHANGED.value]
    assert items[0]["related_type"] == "quote"


def test_quote_status_change_without_an_account_is_silently_skipped(client, admin_headers):
    """Quotes are public — there may be no user to notify, and that's fine."""
    quote = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "No Account",
            "email": "no_account_anywhere@example.com",
            "phone": "0700000000",
            "project_title": "Anonymous quote",
            "project_description": "No account behind this",
        },
    ).json()

    resp = client.patch(
        f"/api/v1/quote-requests/{quote['id']}", json={"status": "REVIEWING"}, headers=admin_headers
    )
    assert resp.status_code == 200


def test_milestone_completion_notifies_the_project_client(client, admin_headers):
    c = _create_client("notify_milestone@example.com")
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

    client.patch(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )

    types = [n["type"] for n in _notifications_for(client, _auth(c))]
    assert NotificationType.MILESTONE_COMPLETED.value in types

    # Re-saving an already completed milestone must not notify a second time.
    client.patch(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )
    again = [n["type"] for n in _notifications_for(client, _auth(c))]
    assert again.count(NotificationType.MILESTONE_COMPLETED.value) == 1


def test_issued_invoice_notifies_client_but_draft_does_not(client, admin_headers):
    c = _create_client("notify_invoice@example.com")

    client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "100.00", "status": "DRAFT"},
        headers=admin_headers,
    )
    assert _notifications_for(client, _auth(c)) == []

    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()

    items = _notifications_for(client, _auth(c))
    assert [n["type"] for n in items] == [NotificationType.INVOICE_CREATED.value]
    assert items[0]["related_type"] == "invoice"
    assert items[0]["related_id"] == invoice["id"]


def test_payment_recording_notifies_the_client(client, admin_headers):
    c = _create_client("notify_payment@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()

    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "200.00", "method": "CASH"},
        headers=admin_headers,
    )

    types = [n["type"] for n in _notifications_for(client, _auth(c))]
    assert NotificationType.PAYMENT_RECORDED.value in types


# --- the non-fatal contract -------------------------------------------------


def test_payment_still_succeeds_when_notification_emit_fails(
    client, admin_headers, monkeypatch
):
    """
    The whole point of the non-fatal wrapper: if the notification insert blows
    up, the payment must still be recorded and returned.
    """
    c = _create_client("notify_failsafe@example.com")
    invoice = client.post(
        "/api/v1/invoices",
        json={"client_id": c.id, "subtotal": "500.00", "status": "SENT"},
        headers=admin_headers,
    ).json()

    from app.crud import notification as notification_crud

    def _boom(*args, **kwargs):
        raise RuntimeError("notification backend exploded")

    monkeypatch.setattr(notification_crud, "create", _boom)

    resp = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        json={"amount": "250.00", "method": "CASH"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text

    after = client.get(f"/api/v1/invoices/{invoice['id']}", headers=admin_headers).json()
    assert after["amount_paid"] == "250.00"
    assert after["status"] == "PARTIALLY_PAID"
    # The payment notification was dropped (the INVOICE_CREATED one predates
    # the patched failure, so it is still there).
    types = [n["type"] for n in _notifications_for(client, _auth(c))]
    assert NotificationType.PAYMENT_RECORDED.value not in types
    assert types == [NotificationType.INVOICE_CREATED.value]


def test_project_creation_still_succeeds_when_notification_emit_fails(
    client, admin_headers, monkeypatch
):
    c = _create_client("notify_failsafe2@example.com")

    from app.crud import notification as notification_crud

    monkeypatch.setattr(
        notification_crud, "create", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    )

    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Survives", "description": "d"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Survives"


# --- scoping ----------------------------------------------------------------


def test_client_sees_only_their_own_notifications(client, admin_headers):
    c1 = _create_client("notify_mine@example.com")
    c2 = _create_client("notify_theirs@example.com")
    client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "C1 Project", "description": "d"},
        headers=admin_headers,
    )
    client.post(
        "/api/v1/projects",
        json={"client_id": c2.id, "title": "C2 Project", "description": "d"},
        headers=admin_headers,
    )

    c1_items = _notifications_for(client, _auth(c1))
    c2_items = _notifications_for(client, _auth(c2))
    assert len(c1_items) == 1
    assert len(c2_items) == 1
    assert c1_items[0]["id"] != c2_items[0]["id"]


def test_marking_another_users_notification_returns_404(client, admin_headers):
    c1 = _create_client("notify_owner@example.com")
    c2 = _create_client("notify_intruder@example.com")
    client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "Owned", "description": "d"},
        headers=admin_headers,
    )
    target = _notifications_for(client, _auth(c1))[0]

    resp = client.patch(f"/api/v1/notifications/{target['id']}/read", headers=_auth(c2))
    assert resp.status_code == 404


def test_notifications_require_authentication(client):
    assert client.get("/api/v1/notifications").status_code == 401
    assert client.get("/api/v1/notifications/unread-count").status_code == 401
    assert client.patch("/api/v1/notifications/read-all").status_code == 401


# --- unread count, mark read ------------------------------------------------


def test_unread_count_tracks_reads(client, admin_headers):
    c = _create_client("notify_count@example.com")
    for title in ("P1", "P2", "P3"):
        client.post(
            "/api/v1/projects",
            json={"client_id": c.id, "title": title, "description": "d"},
            headers=admin_headers,
        )

    headers = _auth(c)
    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"unread": 3}

    first = _notifications_for(client, headers)[0]
    marked = client.patch(f"/api/v1/notifications/{first['id']}/read", headers=headers)
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True
    assert marked.json()["read_at"] is not None

    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"unread": 2}
    assert len(_notifications_for(client, headers, unread_only=True)) == 2

    all_read = client.patch("/api/v1/notifications/read-all", headers=headers)
    assert all_read.status_code == 200
    assert all_read.json() == {"updated": 2}
    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"unread": 0}
    assert _notifications_for(client, headers, unread_only=True) == []


def test_read_all_only_affects_the_caller(client, admin_headers):
    c1 = _create_client("notify_ra1@example.com")
    c2 = _create_client("notify_ra2@example.com")
    for c in (c1, c2):
        client.post(
            "/api/v1/projects",
            json={"client_id": c.id, "title": "P", "description": "d"},
            headers=admin_headers,
        )

    client.patch("/api/v1/notifications/read-all", headers=_auth(c1))

    assert client.get("/api/v1/notifications/unread-count", headers=_auth(c1)).json()["unread"] == 0
    assert client.get("/api/v1/notifications/unread-count", headers=_auth(c2)).json()["unread"] == 1


def test_list_is_newest_first_and_paginates(client, admin_headers):
    c = _create_client("notify_page@example.com")
    for title in ("First", "Second", "Third"):
        client.post(
            "/api/v1/projects",
            json={"client_id": c.id, "title": title, "description": "d"},
            headers=admin_headers,
        )

    headers = _auth(c)
    page = _notifications_for(client, headers, limit=2)
    assert len(page) == 2
    assert "Third" in page[0]["message"]  # newest first

    second_page = _notifications_for(client, headers, limit=2, offset=2)
    assert len(second_page) == 1
    assert "First" in second_page[0]["message"]


# --- no public create surface ----------------------------------------------


@pytest.mark.parametrize("method", ["post", "put"])
def test_there_is_no_public_create_notification_endpoint(client, admin_headers, method):
    """Notifications are system-emitted; clients must not be able to forge them."""
    resp = getattr(client, method)(
        "/api/v1/notifications",
        json={
            "user_id": 1,
            "type": "PROJECT_CREATED",
            "title": "Forged",
            "message": "Should not exist",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 405, f"{method.upper()} /notifications should not be routable"


def test_openapi_exposes_no_notification_write_schema(client):
    spec = client.get("/openapi.json").json()
    methods = set(spec["paths"]["/api/v1/notifications"].keys())
    assert methods == {"get"}, methods
    assert "NotificationCreate" not in spec["components"]["schemas"]
