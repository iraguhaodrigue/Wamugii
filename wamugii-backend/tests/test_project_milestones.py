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
            UserCreate(full_name=full_name, email=email, password="testpass123"),
            role=Role.CLIENT,
        )
    finally:
        db.close()


def _client_auth_headers(user) -> dict:
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_create_milestone(client, admin_headers):
    """1. ADMIN can create a milestone"""
    c = _create_client("testclient@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial phase"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Phase 1"
    assert body["status"] == "PENDING"
    assert body["project_id"] == project_id


def test_staff_can_create_milestone(client, admin_headers, staff_headers):
    """2. STAFF can create a milestone"""
    c = _create_client("testclient2@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 2", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Design Phase", "description": "UI/UX design"},
        headers=staff_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Design Phase"


def test_client_cannot_create_milestone(client, admin_headers, client_headers):
    """3. CLIENT cannot create a milestone"""
    c = _create_client("testclient3@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 3", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial phase"},
        headers=client_headers,
    )
    assert resp.status_code == 403


def test_milestone_cannot_be_created_for_invalid_project(client, admin_headers):
    """4. Milestone cannot be created for invalid project"""
    resp = client.post(
        "/api/v1/projects/99999/milestones",
        json={"title": "Phase 1", "description": "Initial phase"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_milestone_cannot_be_created_for_inactive_project(client, admin_headers):
    """5. Milestone cannot be created for inactive project"""
    c = _create_client("testclient4@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 4", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    # Deactivate the project
    client.delete(f"/api/v1/projects/{project_id}", headers=admin_headers)

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial phase"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_get_single_milestone_for_inactive_project_returns_404(client, admin_headers):
    """5b. GET single milestone is blocked once the parent project is deactivated"""
    c = _create_client("testclient4b@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 4b", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    # Deactivate the project
    client.delete(f"/api/v1/projects/{project_id}", headers=admin_headers)

    resp = client.get(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_milestones_list_correctly(client, admin_headers):
    """6. Milestones list correctly"""
    c = _create_client("testclient5@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 5", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    # Create multiple milestones
    for i in range(3):
        client.post(
            f"/api/v1/projects/{project_id}/milestones",
            json={"title": f"Phase {i+1}", "description": f"Phase {i+1}"},
            headers=admin_headers,
        )

    resp = client.get(
        f"/api/v1/projects/{project_id}/milestones",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_client_sees_milestones_only_for_own_project(client, admin_headers):
    """7. CLIENT sees milestones only for their own project"""
    c1 = _create_client("owner1@example.com")
    c2 = _create_client("owner2@example.com")

    # Create projects for both clients
    resp1 = client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "Project 1", "description": "Test"},
        headers=admin_headers,
    )
    project1_id = resp1.json()["id"]

    resp2 = client.post(
        "/api/v1/projects",
        json={"client_id": c2.id, "title": "Project 2", "description": "Test"},
        headers=admin_headers,
    )
    project2_id = resp2.json()["id"]

    # Add milestone to both projects
    client.post(
        f"/api/v1/projects/{project1_id}/milestones",
        json={"title": "M1", "description": "Milestone 1"},
        headers=admin_headers,
    )
    client.post(
        f"/api/v1/projects/{project2_id}/milestones",
        json={"title": "M2", "description": "Milestone 2"},
        headers=admin_headers,
    )

    # c1 should see only project1 milestones
    c1_headers = _client_auth_headers(c1)
    resp = client.get(
        f"/api/v1/projects/{project1_id}/milestones",
        headers=c1_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # c1 should NOT see project2 milestones
    resp = client.get(
        f"/api/v1/projects/{project2_id}/milestones",
        headers=c1_headers,
    )
    assert resp.status_code == 404


def test_client_cannot_view_another_clients_milestones(client, admin_headers):
    """8. CLIENT cannot view another client's milestones"""
    c1 = _create_client("client1@example.com")
    c2 = _create_client("client2@example.com")

    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "Project C1", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "M1", "description": "Milestone 1"},
        headers=admin_headers,
    )

    c2_headers = _client_auth_headers(c2)
    resp = client.get(
        f"/api/v1/projects/{project_id}/milestones",
        headers=c2_headers,
    )
    assert resp.status_code == 404


def test_admin_can_update_milestone(client, admin_headers):
    """9. ADMIN can update milestone"""
    c = _create_client("testclient6@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 6", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        json={"title": "Phase 1 Updated"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Phase 1 Updated"


def test_staff_can_update_milestone(client, admin_headers, staff_headers):
    """10. STAFF can update milestone"""
    c = _create_client("testclient7@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 7", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        json={"description": "Updated description"},
        headers=staff_headers,
    )
    assert resp.status_code == 200


def test_client_cannot_update_milestone(client, admin_headers, client_headers):
    """11. CLIENT cannot update milestone"""
    c = _create_client("testclient8@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 8", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        json={"title": "Updated"},
        headers=client_headers,
    )
    assert resp.status_code == 403


def test_completed_status_automatically_sets_completed_at(client, admin_headers):
    """12. COMPLETED status automatically sets completed_at"""
    c = _create_client("testclient9@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 9", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]
    assert resp.json()["completed_at"] is None

    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["completed_at"] is not None


def test_moving_away_from_completed_handles_completed_at(client, admin_headers):
    """13. Moving away from COMPLETED handles completed_at correctly"""
    c = _create_client("testclient10@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 10", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial", "status": "COMPLETED"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        json={"status": "IN_PROGRESS"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["completed_at"] is None


def test_invalid_dates_are_rejected(client, admin_headers):
    """14. Invalid dates are rejected"""
    c = _create_client("testclient11@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 11", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={
            "title": "Phase 1",
            "description": "Initial",
            "start_date": "2026-12-31T00:00:00Z",
            "due_date": "2026-01-01T00:00:00Z",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_admin_can_soft_delete_milestone(client, admin_headers):
    """15. ADMIN can soft-delete milestone"""
    c = _create_client("testclient12@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 12", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    resp = client.delete(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_staff_cannot_delete_milestone(client, admin_headers, staff_headers):
    """16. STAFF cannot delete milestone"""
    c = _create_client("testclient13@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 13", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Phase 1", "description": "Initial"},
        headers=admin_headers,
    )
    milestone_id = resp.json()["id"]

    resp = client.delete(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}",
        headers=staff_headers,
    )
    assert resp.status_code == 403


def test_reordering_milestones_works(client, admin_headers):
    """17. Reordering milestones works"""
    c = _create_client("testclient14@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 14", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    # Create 3 milestones
    ids = []
    for i in range(3):
        resp = client.post(
            f"/api/v1/projects/{project_id}/milestones",
            json={"title": f"Phase {i+1}", "description": f"Phase {i+1}"},
            headers=admin_headers,
        )
        ids.append(resp.json()["id"])

    # Reorder them
    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/reorder",
        json={
            "milestones": [
                {"id": ids[2], "display_order": 1},
                {"id": ids[1], "display_order": 2},
                {"id": ids[0], "display_order": 3},
            ]
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200

    # Verify order changed
    resp = client.get(
        f"/api/v1/projects/{project_id}/milestones",
        headers=admin_headers,
    )
    assert resp.json()[0]["id"] == ids[2]
    assert resp.json()[1]["id"] == ids[1]
    assert resp.json()[2]["id"] == ids[0]


def test_reordering_with_invalid_milestone_ids_fails(client, admin_headers):
    """18. Reordering with invalid milestone IDs fails safely"""
    c = _create_client("testclient15@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 15", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/milestones/reorder",
        json={
            "milestones": [
                {"id": 99999, "display_order": 1},
            ]
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_project_progress_calculation_is_correct(client, admin_headers):
    """19. Project progress calculation is correct"""
    c = _create_client("testclient16@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 16", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    # Create 6 milestones with different statuses
    statuses = [
        "COMPLETED",
        "COMPLETED",
        "IN_PROGRESS",
        "PENDING",
        "PENDING",
        "PENDING",
    ]
    for status in statuses:
        client.post(
            f"/api/v1/projects/{project_id}/milestones",
            json={"title": f"M {status}", "description": "Test", "status": status},
            headers=admin_headers,
        )

    resp = client.get(
        f"/api/v1/projects/{project_id}/progress",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_milestones"] == 6
    assert body["completed_milestones"] == 2
    assert body["in_progress_milestones"] == 1
    assert body["pending_milestones"] == 3
    assert body["progress_percentage"] == 33.33


def test_project_with_zero_milestones_returns_0_percent_progress(
    client, admin_headers
):
    """20. Project with zero milestones returns 0% progress"""
    c = _create_client("testclient17@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Test Project 17", "description": "Test"},
        headers=admin_headers,
    )
    project_id = resp.json()["id"]

    resp = client.get(
        f"/api/v1/projects/{project_id}/progress",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_milestones"] == 0
    assert body["progress_percentage"] == 0.0


def test_client_can_view_progress_only_for_own_project(client, admin_headers):
    """21. CLIENT can view progress only for their own project"""
    c1 = _create_client("client1b@example.com")
    c2 = _create_client("client2b@example.com")

    resp1 = client.post(
        "/api/v1/projects",
        json={"client_id": c1.id, "title": "Project C1", "description": "Test"},
        headers=admin_headers,
    )
    project1_id = resp1.json()["id"]

    resp2 = client.post(
        "/api/v1/projects",
        json={"client_id": c2.id, "title": "Project C2", "description": "Test"},
        headers=admin_headers,
    )
    project2_id = resp2.json()["id"]

    c1_headers = _client_auth_headers(c1)

    # c1 can view progress for their own project
    resp = client.get(
        f"/api/v1/projects/{project1_id}/progress",
        headers=c1_headers,
    )
    assert resp.status_code == 200

    # c1 cannot view progress for another project
    resp = client.get(
        f"/api/v1/projects/{project2_id}/progress",
        headers=c1_headers,
    )
    assert resp.status_code == 404


def test_existing_tests_continue_passing(client, admin_headers):
    """22. Existing tests continue passing"""
    # Create a simple project
    c = _create_client("testclientfinal@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Final Test", "description": "Test"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Final Test"
