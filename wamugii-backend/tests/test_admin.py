from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


def _create_user(role: Role, email: str, full_name: str = "Test User"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db, UserCreate(full_name=full_name, email=email, password="password123"), role=role
        )
    finally:
        db.close()


def test_dashboard_as_admin(client, admin_headers):
    resp = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["users"] == {"total": 1, "clients": 0, "staff": 0, "admins": 1}
    assert body["services"] == {"total": 0, "active": 0}
    assert body["projects"]["total"] == 0
    assert body["quotes"]["pending"] == 0


def test_dashboard_as_client_forbidden(client, client_headers):
    resp = client.get("/api/v1/admin/dashboard", headers=client_headers)
    assert resp.status_code == 403


def test_dashboard_as_staff_forbidden(client, staff_headers):
    resp = client.get("/api/v1/admin/dashboard", headers=staff_headers)
    assert resp.status_code == 403


def test_dashboard_unauthenticated(client):
    resp = client.get("/api/v1/admin/dashboard")
    assert resp.status_code == 401


def test_list_search_filter_users(client, admin_headers):
    _create_user(Role.STAFF, "staffer@example.com", full_name="Sammy Staff")
    _create_user(Role.CLIENT, "clientperson@example.com", full_name="Cathy Client")

    all_users = client.get("/api/v1/admin/users", headers=admin_headers).json()
    assert len(all_users) == 3

    by_role = client.get(
        "/api/v1/admin/users", params={"role": "STAFF"}, headers=admin_headers
    ).json()
    assert {u["email"] for u in by_role} == {"staffer@example.com"}

    by_search = client.get(
        "/api/v1/admin/users", params={"search": "cathy"}, headers=admin_headers
    ).json()
    assert {u["email"] for u in by_search} == {"clientperson@example.com"}


def test_deactivate_user(client, admin_headers):
    target = _create_user(Role.CLIENT, "todeactivate@example.com")
    resp = client.delete(f"/api/v1/admin/users/{target.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_cannot_remove_last_active_admin(client, admin_headers):
    admins = client.get(
        "/api/v1/admin/users", params={"role": "ADMIN"}, headers=admin_headers
    ).json()
    assert len(admins) == 1
    admin_id = admins[0]["id"]

    resp = client.delete(f"/api/v1/admin/users/{admin_id}", headers=admin_headers)
    assert resp.status_code == 409

    resp2 = client.patch(
        f"/api/v1/admin/users/{admin_id}", json={"role": "CLIENT"}, headers=admin_headers
    )
    assert resp2.status_code == 409

    resp3 = client.patch(
        f"/api/v1/admin/users/{admin_id}", json={"is_active": False}, headers=admin_headers
    )
    assert resp3.status_code == 409
