from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


def _create_client(email: str, full_name: str = "Test Client"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password="password123"),
            role=Role.CLIENT,
        )
    finally:
        db.close()


def _client_auth_headers(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _accepted_quote(client, admin_headers, email: str) -> dict:
    created = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Quoter",
            "email": email,
            "phone": "0700000000",
            "project_title": "Website revamp",
            "project_description": "Redo the marketing site",
        },
    ).json()
    client.patch(
        f"/api/v1/quote-requests/{created['id']}",
        json={"status": "ACCEPTED"},
        headers=admin_headers,
    )
    return created


def test_admin_can_create_project(client, admin_headers):
    c = _create_client("clienta@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "New Website", "description": "Build a new site"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PENDING"
    assert body["priority"] == "MEDIUM"
    assert body["client_id"] == c.id


def test_staff_can_create_project(client, staff_headers):
    c = _create_client("clientb@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "IT Consultancy", "description": "Assess infra"},
        headers=staff_headers,
    )
    assert resp.status_code == 201


def test_client_cannot_create_project(client, client_headers):
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": 1, "title": "X", "description": "Y"},
        headers=client_headers,
    )
    assert resp.status_code == 403


def test_client_sees_only_own_projects(client, admin_headers):
    c1 = _create_client("owner1@example.com")
    c2 = _create_client("owner2@example.com")
    client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "Project 1", "description": "d"},
        headers=admin_headers,
    )
    client.post(
        "/api/v1/projects",
        json={"client_id": c2.id, "title": "Project 2", "description": "d"},
        headers=admin_headers,
    )

    resp = client.get("/api/v1/projects", headers=_client_auth_headers(c1))
    assert resp.status_code == 200
    titles = [p["title"] for p in resp.json()]
    assert titles == ["Project 1"]


def test_client_cannot_access_another_clients_project(client, admin_headers):
    c1 = _create_client("ownerA@example.com")
    c2 = _create_client("ownerB@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "Private Project", "description": "d"},
        headers=admin_headers,
    ).json()

    resp = client.get(f"/api/v1/projects/{created['id']}", headers=_client_auth_headers(c2))
    assert resp.status_code == 404


def test_admin_can_list_all_projects(client, admin_headers):
    c1 = _create_client("listc1@example.com")
    c2 = _create_client("listc2@example.com")
    client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "P1", "description": "d"},
        headers=admin_headers,
    )
    client.post(
        "/api/v1/projects",
        json={"client_id": c2.id, "title": "P2", "description": "d"},
        headers=admin_headers,
    )

    resp = client.get("/api/v1/projects", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_invalid_client_id_rejected(client, admin_headers):
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": 999999, "title": "X", "description": "Y"},
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_invalid_service_id_rejected(client, admin_headers):
    c = _create_client("svcclient@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "service_id": 999999, "title": "X", "description": "Y"},
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_invalid_quote_request_id_rejected(client, admin_headers):
    c = _create_client("qclient@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "quote_request_id": 999999, "title": "X", "description": "Y"},
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_project_from_non_accepted_quote_rejected(client, admin_headers):
    created = client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Pending Quoter",
            "email": "pending@example.com",
            "phone": "0711111111",
            "project_title": "Pending Idea",
            "project_description": "Not accepted yet",
        },
    ).json()
    resp = client.post(
        f"/api/v1/quote-requests/{created['id']}/create-project", headers=admin_headers
    )
    assert resp.status_code == 422


def test_project_from_accepted_quote_succeeds(client, admin_headers):
    _create_client("acceptedowner@example.com")
    quote = _accepted_quote(client, admin_headers, email="acceptedowner@example.com")
    resp = client.post(
        f"/api/v1/quote-requests/{quote['id']}/create-project", headers=admin_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["quote_request_id"] == quote["id"]
    assert body["title"] == quote["project_title"]


def test_duplicate_project_from_same_quote_prevented(client, admin_headers):
    _create_client("dupowner@example.com")
    quote = _accepted_quote(client, admin_headers, email="dupowner@example.com")
    first = client.post(
        f"/api/v1/quote-requests/{quote['id']}/create-project", headers=admin_headers
    )
    assert first.status_code == 201
    second = client.post(
        f"/api/v1/quote-requests/{quote['id']}/create-project", headers=admin_headers
    )
    assert second.status_code == 409


def test_admin_can_update_project(client, admin_headers):
    c = _create_client("updateclient@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Old", "description": "d"},
        headers=admin_headers,
    ).json()
    resp = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"status": "IN_PROGRESS", "priority": "HIGH"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "IN_PROGRESS"
    assert body["priority"] == "HIGH"


def test_client_cannot_update_project(client, admin_headers):
    c = _create_client("noupdateclient@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Old", "description": "d"},
        headers=admin_headers,
    ).json()
    resp = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"status": "IN_PROGRESS"},
        headers=_client_auth_headers(c),
    )
    assert resp.status_code == 403


def test_admin_can_deactivate_project(client, admin_headers):
    c = _create_client("deactivateclient@example.com")
    created = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Old", "description": "d"},
        headers=admin_headers,
    ).json()
    resp = client.delete(f"/api/v1/projects/{created['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    listed = client.get("/api/v1/projects", headers=admin_headers).json()
    assert all(p["id"] != created["id"] for p in listed)


def test_dashboard_project_statistics(client, admin_headers):
    c = _create_client("dashclient@example.com")
    p1 = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Dash P1", "description": "d"},
        headers=admin_headers,
    ).json()
    client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Dash P2", "description": "d"},
        headers=admin_headers,
    )
    client.delete(f"/api/v1/projects/{p1['id']}", headers=admin_headers)

    resp = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["projects"]["total"] == 2
    assert body["projects"]["active"] == 1
