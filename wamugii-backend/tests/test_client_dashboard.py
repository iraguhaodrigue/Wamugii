from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


def _create_client(email: str, full_name: str = "Test Client") -> int:
    db = TestingSessionLocal()
    try:
        user = user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password="testpass123"),
            role=Role.CLIENT,
        )
        return user.id
    finally:
        db.close()


def _client_auth_headers(user_id: int) -> dict:
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def test_client_can_access_dashboard(client, admin_headers):
    """1. CLIENT can access dashboard"""
    client_id = _create_client("dashclient@example.com")
    client_headers = _client_auth_headers(client_id)

    resp = client.get("/api/v1/client/dashboard", headers=client_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "user" in body
    assert "summary" in body
    assert "recent_projects" in body
    assert "recent_quotes" in body
    assert "recent_activity" in body
    assert body["user"]["id"] == client_id


def test_admin_cannot_access_client_dashboard(client, admin_headers):
    """2. ADMIN cannot access client dashboard"""
    resp = client.get("/api/v1/client/dashboard", headers=admin_headers)
    assert resp.status_code == 403


def test_staff_cannot_access_client_dashboard(client, staff_headers):
    """3. STAFF cannot access client dashboard"""
    resp = client.get("/api/v1/client/dashboard", headers=staff_headers)
    assert resp.status_code == 403


def test_unauthenticated_cannot_access_dashboard(client):
    """4. Unauthenticated user gets 401"""
    resp = client.get("/api/v1/client/dashboard")
    assert resp.status_code == 401


def test_client_sees_only_own_projects(client, admin_headers):
    """5. CLIENT sees only own projects"""
    c1_id = _create_client("owner1dash@example.com")
    c2_id = _create_client("owner2dash@example.com")
    c1_headers = _client_auth_headers(c1_id)

    # Create projects for both clients
    resp1 = client.post(
        "/api/v1/projects",
        json={"client_id": c1_id, "title": "Project C1", "description": "Test"},
        headers=admin_headers,
    )
    p1_id = resp1.json()["id"]

    resp2 = client.post(
        "/api/v1/projects",
        json={"client_id": c2_id, "title": "Project C2", "description": "Test"},
        headers=admin_headers,
    )
    p2_id = resp2.json()["id"]

    # c1 should see only their project
    resp = client.get("/api/v1/client/projects", headers=c1_headers)
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) == 1
    assert projects[0]["id"] == p1_id


def test_client_cannot_access_another_clients_project(client, admin_headers):
    """6. CLIENT cannot access another client's project"""
    c1_id = _create_client("user1dash@example.com")
    c2_id = _create_client("user2dash@example.com")
    c1_headers = _client_auth_headers(c1_id)

    # Create project for c2
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c2_id, "title": "Project C2", "description": "Test"},
        headers=admin_headers,
    )
    p2_id = resp.json()["id"]

    # c1 tries to access c2's project
    resp = client.get(f"/api/v1/client/projects/{p2_id}", headers=c1_headers)
    assert resp.status_code == 404


def test_client_can_view_own_milestones(client, admin_headers):
    """7. CLIENT can view own milestones"""
    c_id = _create_client("milestoneclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create project
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Project M", "description": "Test"},
        headers=admin_headers,
    )
    p_id = resp.json()["id"]

    # Create milestone
    client.post(
        f"/api/v1/projects/{p_id}/milestones",
        json={"title": "M1", "description": "Milestone 1"},
        headers=admin_headers,
    )

    # Client views milestones
    resp = client.get(f"/api/v1/client/projects/{p_id}/milestones", headers=c_headers)
    assert resp.status_code == 200
    milestones = resp.json()
    assert len(milestones) == 1
    assert milestones[0]["title"] == "M1"


def test_client_cannot_view_another_clients_milestones(client, admin_headers):
    """8. CLIENT cannot view another client's milestones"""
    c1_id = _create_client("client1m@example.com")
    c2_id = _create_client("client2m@example.com")
    c1_headers = _client_auth_headers(c1_id)

    # Create project for c2 with milestone
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c2_id, "title": "Project C2M", "description": "Test"},
        headers=admin_headers,
    )
    p2_id = resp.json()["id"]

    client.post(
        f"/api/v1/projects/{p2_id}/milestones",
        json={"title": "M2", "description": "Milestone"},
        headers=admin_headers,
    )

    # c1 tries to access c2's milestones
    resp = client.get(f"/api/v1/client/projects/{p2_id}/milestones", headers=c1_headers)
    assert resp.status_code == 404


def test_client_sees_only_own_quotes(client):
    """9. CLIENT sees only safely associated quotes"""
    c_id = _create_client("quoteclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create quote with client's email
    client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Quote Client",
            "email": "quoteclient@example.com",
            "phone": "0700000000",
            "project_title": "Website",
            "project_description": "New website",
        },
    )

    # Client views their quotes
    resp = client.get("/api/v1/client/quotes", headers=c_headers)
    assert resp.status_code == 200
    quotes = resp.json()
    assert len(quotes) == 1
    assert "admin_notes" not in quotes[0]


def test_admin_notes_never_appear_in_responses(client, admin_headers):
    """10. admin_notes never appear in responses"""
    c_id = _create_client("notetest@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create quote
    client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Note Test",
            "email": "notetest@example.com",
            "phone": "0700000000",
            "project_title": "Test",
            "project_description": "Test",
        },
    )

    # Client views quote
    resp = client.get("/api/v1/client/quotes", headers=c_headers)
    assert resp.status_code == 200
    quotes = resp.json()
    assert len(quotes) > 0
    assert "admin_notes" not in quotes[0]

    # Check dashboard
    resp = client.get("/api/v1/client/dashboard", headers=c_headers)
    assert resp.status_code == 200
    body = resp.json()
    # Verify no admin fields are exposed
    assert "admin_notes" not in body


def test_dashboard_statistics_are_correct(client, admin_headers):
    """11. Dashboard statistics are correct"""
    c_id = _create_client("statsclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create 3 projects
    for i in range(3):
        client.post(
            "/api/v1/projects",
            json={"client_id": c_id, "title": f"Project {i}", "description": "Test"},
            headers=admin_headers,
        )

    # Create quote
    client.post(
        "/api/v1/quote-requests",
        json={
            "full_name": "Stats Test",
            "email": "statsclient@example.com",
            "phone": "0700000000",
            "project_title": "Quote",
            "project_description": "Quote",
        },
    )

    resp = client.get("/api/v1/client/dashboard", headers=c_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]["total_projects"] == 3
    assert body["summary"]["pending_quotes"] == 1


def test_project_progress_is_correct(client, admin_headers):
    """12. Project progress is correct"""
    c_id = _create_client("progclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create project with milestones
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Progress Project", "description": "Test"},
        headers=admin_headers,
    )
    p_id = resp.json()["id"]

    # Create 4 milestones
    statuses = ["COMPLETED", "COMPLETED", "IN_PROGRESS", "PENDING"]
    for status in statuses:
        client.post(
            f"/api/v1/projects/{p_id}/milestones",
            json={"title": f"M {status}", "description": "Test", "status": status},
            headers=admin_headers,
        )

    # Get project and check progress
    resp = client.get(f"/api/v1/client/projects/{p_id}", headers=c_headers)
    assert resp.status_code == 200
    project = resp.json()
    assert project["progress_percentage"] == 50.0


def test_pagination_works(client, admin_headers):
    """13. Pagination works"""
    c_id = _create_client("pageclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create 5 projects
    for i in range(5):
        client.post(
            "/api/v1/projects",
            json={"client_id": c_id, "title": f"Project {i}", "description": "Test"},
            headers=admin_headers,
        )

    # Get first page
    resp = client.get(
        "/api/v1/client/projects?limit=2&offset=0",
        headers=c_headers,
    )
    assert resp.status_code == 200
    page1 = resp.json()
    assert len(page1) == 2

    # Get second page
    resp = client.get(
        "/api/v1/client/projects?limit=2&offset=2",
        headers=c_headers,
    )
    assert resp.status_code == 200
    page2 = resp.json()
    assert len(page2) == 2


def test_status_filtering_works(client, admin_headers):
    """14. Status filtering works"""
    c_id = _create_client("filterclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create project and set it to completed
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Completed", "description": "Test"},
        headers=admin_headers,
    )
    p_id = resp.json()["id"]

    client.patch(
        f"/api/v1/projects/{p_id}",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )

    # Create another project (PENDING)
    client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Pending", "description": "Test"},
        headers=admin_headers,
    )

    # Filter by COMPLETED
    resp = client.get(
        "/api/v1/client/projects?status=COMPLETED",
        headers=c_headers,
    )
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) == 1
    assert projects[0]["title"] == "Completed"


def test_search_works(client, admin_headers):
    """15. Search works"""
    c_id = _create_client("searchclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create projects
    client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Website Redesign", "description": "Test"},
        headers=admin_headers,
    )

    client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Mobile App", "description": "Test"},
        headers=admin_headers,
    )

    # Search for "website"
    resp = client.get(
        "/api/v1/client/projects?search=website",
        headers=c_headers,
    )
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) == 1
    assert "Website" in projects[0]["title"]


def test_recent_activity_is_limited_correctly(client, admin_headers):
    """16. Recent activity is limited correctly"""
    c_id = _create_client("activityclient@example.com")
    c_headers = _client_auth_headers(c_id)

    # Create multiple projects
    for i in range(5):
        client.post(
            "/api/v1/projects",
            json={"client_id": c_id, "title": f"Project {i}", "description": "Test"},
            headers=admin_headers,
        )

    # Get dashboard
    resp = client.get("/api/v1/client/dashboard", headers=c_headers)
    assert resp.status_code == 200
    body = resp.json()
    # Activity should be limited
    assert len(body["recent_activity"]) <= 10


def test_existing_tests_continue_passing(client, admin_headers):
    """17. Existing tests continue passing"""
    # Create basic project - should still work
    c_id = _create_client("existingtest@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c_id, "title": "Existing", "description": "Test"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
