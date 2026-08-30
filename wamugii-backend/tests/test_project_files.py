from pathlib import Path

import pytest

from app.core.config import settings
from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.project_file import ProjectFile
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def _tmp_upload_dir(tmp_path, monkeypatch):
    """Redirect all file storage to a pytest tmp dir so tests never touch uploads/."""
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    yield


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


def _create_project(client, admin_headers, client_id, title="Test Project"):
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": client_id, "title": title, "description": "Test"},
        headers=admin_headers,
    )
    return resp.json()["id"]


def _pdf_bytes() -> bytes:
    return b"%PDF-1.4\n%fake pdf content for testing\n"


def _png_bytes() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"fake png data for testing"


def test_admin_can_upload_file(client, admin_headers):
    """1. ADMIN can upload a file"""
    c = _create_client("fileclient1@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("requirements.pdf", _pdf_bytes(), "application/pdf")},
        data={"category": "REQUIREMENT", "description": "Initial requirements"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["original_filename"] == "requirements.pdf"
    assert body["category"] == "REQUIREMENT"
    assert body["file_size"] > 0
    assert body["uploaded_by"] is not None


def test_staff_can_upload_file(client, admin_headers, staff_headers):
    """2. STAFF can upload a file (default category is DOCUMENT)"""
    c = _create_client("fileclient2@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("design.png", _png_bytes(), "image/png")},
        headers=staff_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["category"] == "DOCUMENT"


def test_client_can_upload_to_own_project(client, admin_headers):
    """3. CLIENT can upload to their own project"""
    c = _create_client("fileclient3@example.com")
    project_id = _create_project(client, admin_headers, c.id)
    c_headers = _client_auth_headers(c)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("mydoc.pdf", _pdf_bytes(), "application/pdf")},
        headers=c_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["uploaded_by"] == c.id


def test_client_cannot_upload_to_another_project(client, admin_headers):
    """4. CLIENT cannot upload to another client's project"""
    c1 = _create_client("fileclient4a@example.com")
    c2 = _create_client("fileclient4b@example.com")
    project_id = _create_project(client, admin_headers, c1.id)
    c2_headers = _client_auth_headers(c2)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("hack.pdf", _pdf_bytes(), "application/pdf")},
        headers=c2_headers,
    )
    assert resp.status_code == 404


def test_upload_rejected_for_invalid_project(client, admin_headers):
    """5. Upload rejected for a nonexistent project"""
    resp = client.post(
        "/api/v1/projects/99999/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_upload_rejected_for_inactive_project(client, admin_headers):
    """6. Upload rejected for an inactive project"""
    c = _create_client("fileclient6@example.com")
    project_id = _create_project(client, admin_headers, c.id)
    client.delete(f"/api/v1/projects/{project_id}", headers=admin_headers)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_unsupported_file_type_rejected(client, admin_headers):
    """7. Unsupported / executable file type is rejected"""
    c = _create_client("fileclient7@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("virus.exe", b"MZ\x90\x00", "application/x-msdownload")},
        headers=admin_headers,
    )
    assert resp.status_code == 415


def test_mismatched_extension_and_content_type_rejected(client, admin_headers):
    """8. A declared content-type that doesn't match the extension is rejected"""
    c = _create_client("fileclient8@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("fake.pdf", _pdf_bytes(), "image/png")},
        headers=admin_headers,
    )
    assert resp.status_code == 415


def test_oversized_file_rejected(client, admin_headers, monkeypatch):
    """9. Oversized file is rejected"""
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)
    c = _create_client("fileclient9@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    big_content = b"a" * (2 * 1024 * 1024)
    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("big.pdf", big_content, "application/pdf")},
        headers=admin_headers,
    )
    assert resp.status_code == 413


def test_generated_filename_differs_from_original(client, admin_headers):
    """10. Generated filename differs from original; original is preserved"""
    c = _create_client("fileclient10@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("my original name.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["original_filename"] == "my original name.pdf"

    db = TestingSessionLocal()
    try:
        file_row = db.get(ProjectFile, body["id"])
        assert file_row.stored_filename != "my original name.pdf"
        assert file_row.original_filename == "my original name.pdf"
        physical = Path(settings.UPLOAD_DIR) / file_row.storage_path
        assert physical.is_file()
    finally:
        db.close()


def test_listing_pagination_and_category_filter(client, admin_headers):
    """11. Listing, pagination, and category filter all work; newest first"""
    c = _create_client("fileclient11@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("req.pdf", _pdf_bytes(), "application/pdf")},
        data={"category": "REQUIREMENT"},
        headers=admin_headers,
    )
    client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("design.png", _png_bytes(), "image/png")},
        data={"category": "DESIGN"},
        headers=admin_headers,
    )
    client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("report.pdf", _pdf_bytes(), "application/pdf")},
        data={"category": "REPORT"},
        headers=admin_headers,
    )

    resp = client.get(f"/api/v1/projects/{project_id}/files", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3
    assert resp.json()[0]["original_filename"] == "report.pdf"

    resp = client.get(
        f"/api/v1/projects/{project_id}/files?category=DESIGN", headers=admin_headers
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["original_filename"] == "design.png"

    resp = client.get(
        f"/api/v1/projects/{project_id}/files?limit=2&offset=0", headers=admin_headers
    )
    assert len(resp.json()) == 2


def test_client_cannot_view_or_download_another_projects_files(client, admin_headers):
    """12. CLIENT cannot list, view, or download another project's files"""
    c1 = _create_client("fileclient12a@example.com")
    c2 = _create_client("fileclient12b@example.com")
    project_id = _create_project(client, admin_headers, c1.id)
    c2_headers = _client_auth_headers(c2)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("secret.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    file_id = resp.json()["id"]

    resp = client.get(f"/api/v1/projects/{project_id}/files", headers=c2_headers)
    assert resp.status_code == 404

    resp = client.get(f"/api/v1/projects/{project_id}/files/{file_id}", headers=c2_headers)
    assert resp.status_code == 404

    resp = client.get(
        f"/api/v1/projects/{project_id}/files/{file_id}/download", headers=c2_headers
    )
    assert resp.status_code == 404


def test_authorized_download_works(client, admin_headers):
    """13. Authorized download works and returns the original filename/content"""
    c = _create_client("fileclient13@example.com")
    project_id = _create_project(client, admin_headers, c.id)
    c_headers = _client_auth_headers(c)

    content = _pdf_bytes()
    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("myrequirements.pdf", content, "application/pdf")},
        headers=c_headers,
    )
    file_id = resp.json()["id"]

    resp = client.get(
        f"/api/v1/projects/{project_id}/files/{file_id}/download", headers=c_headers
    )
    assert resp.status_code == 200
    assert resp.content == content
    assert "myrequirements.pdf" in resp.headers.get("content-disposition", "")


def test_metadata_update_authorization(client, admin_headers):
    """14. Owner CLIENT and ADMIN can update metadata"""
    c1 = _create_client("fileclient14a@example.com")
    project_id = _create_project(client, admin_headers, c1.id)
    c1_headers = _client_auth_headers(c1)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=c1_headers,
    )
    file_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/files/{file_id}",
        json={"description": "Updated by owner"},
        headers=c1_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated by owner"

    resp = client.patch(
        f"/api/v1/projects/{project_id}/files/{file_id}",
        json={"category": "REPORT"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["category"] == "REPORT"


def test_client_cannot_update_metadata_of_non_owned_project(client, admin_headers):
    """14b. CLIENT cannot reach a file in a project that isn't theirs"""
    c1 = _create_client("fileclient14c@example.com")
    c2 = _create_client("fileclient14d@example.com")
    project_id = _create_project(client, admin_headers, c1.id)
    c2_headers = _client_auth_headers(c2)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    file_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/files/{file_id}",
        json={"description": "hijack"},
        headers=c2_headers,
    )
    assert resp.status_code == 404


def test_client_cannot_update_staff_uploaded_file(client, admin_headers, staff_headers):
    """14c. CLIENT cannot update metadata of a file uploaded by STAFF in their own project"""
    c = _create_client("fileclient14e@example.com")
    project_id = _create_project(client, admin_headers, c.id)
    c_headers = _client_auth_headers(c)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("staffdoc.pdf", _pdf_bytes(), "application/pdf")},
        headers=staff_headers,
    )
    file_id = resp.json()["id"]

    resp = client.patch(
        f"/api/v1/projects/{project_id}/files/{file_id}",
        json={"description": "client trying to edit"},
        headers=c_headers,
    )
    assert resp.status_code == 404


def test_admin_can_delete_any_file(client, admin_headers, staff_headers):
    """15. ADMIN can delete any file, including one uploaded by STAFF"""
    c = _create_client("fileclient15@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("staffdoc.pdf", _pdf_bytes(), "application/pdf")},
        headers=staff_headers,
    )
    file_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/projects/{project_id}/files/{file_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_staff_cannot_delete_file(client, admin_headers, staff_headers):
    """16. STAFF cannot delete a file (existing convention, matching milestones)"""
    c = _create_client("fileclient16@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    file_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/projects/{project_id}/files/{file_id}", headers=staff_headers)
    assert resp.status_code == 403


def test_client_deletes_only_own_file(client, admin_headers):
    """17. CLIENT can delete a file they uploaded themselves"""
    c = _create_client("fileclient17@example.com")
    project_id = _create_project(client, admin_headers, c.id)
    c_headers = _client_auth_headers(c)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("mine.pdf", _pdf_bytes(), "application/pdf")},
        headers=c_headers,
    )
    file_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/projects/{project_id}/files/{file_id}", headers=c_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_client_cannot_delete_staff_or_admin_file(client, admin_headers, staff_headers):
    """18. CLIENT cannot delete a file uploaded by STAFF or ADMIN in their own project"""
    c = _create_client("fileclient18@example.com")
    project_id = _create_project(client, admin_headers, c.id)
    c_headers = _client_auth_headers(c)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("staff.pdf", _pdf_bytes(), "application/pdf")},
        headers=staff_headers,
    )
    staff_file_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("admin.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    admin_file_id = resp.json()["id"]

    resp = client.delete(
        f"/api/v1/projects/{project_id}/files/{staff_file_id}", headers=c_headers
    )
    assert resp.status_code == 404

    resp = client.delete(
        f"/api/v1/projects/{project_id}/files/{admin_file_id}", headers=c_headers
    )
    assert resp.status_code == 404


def test_soft_delete_hides_from_list_and_blocks_download(client, admin_headers):
    """19. Soft-delete hides the file from the default list and blocks normal download/view"""
    c = _create_client("fileclient19@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    file_id = resp.json()["id"]

    client.delete(f"/api/v1/projects/{project_id}/files/{file_id}", headers=admin_headers)

    resp = client.get(f"/api/v1/projects/{project_id}/files", headers=admin_headers)
    assert resp.status_code == 200
    assert all(f["id"] != file_id for f in resp.json())

    resp = client.get(f"/api/v1/projects/{project_id}/files/{file_id}", headers=admin_headers)
    assert resp.status_code == 404

    resp = client.get(
        f"/api/v1/projects/{project_id}/files/{file_id}/download", headers=admin_headers
    )
    assert resp.status_code == 404


def test_wrong_project_file_pairing_fails_safely(client, admin_headers):
    """20. A file from project A is not reachable via project B's URL"""
    c1 = _create_client("fileclient20a@example.com")
    c2 = _create_client("fileclient20b@example.com")
    project1_id = _create_project(client, admin_headers, c1.id, "Project A")
    project2_id = _create_project(client, admin_headers, c2.id, "Project B")

    resp = client.post(
        f"/api/v1/projects/{project1_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    file_id = resp.json()["id"]

    resp = client.get(f"/api/v1/projects/{project2_id}/files/{file_id}", headers=admin_headers)
    assert resp.status_code == 404

    resp = client.get(
        f"/api/v1/projects/{project2_id}/files/{file_id}/download", headers=admin_headers
    )
    assert resp.status_code == 404


def test_missing_physical_file_handled_gracefully(client, admin_headers):
    """21. A missing physical file on disk is handled gracefully, not a 500"""
    c = _create_client("fileclient21@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    file_id = resp.json()["id"]

    db = TestingSessionLocal()
    try:
        file_row = db.get(ProjectFile, file_id)
        physical = Path(settings.UPLOAD_DIR) / file_row.storage_path
        physical.unlink()
    finally:
        db.close()

    resp = client.get(
        f"/api/v1/projects/{project_id}/files/{file_id}/download", headers=admin_headers
    )
    assert resp.status_code == 404


def test_internal_paths_never_exposed(client, admin_headers):
    """22. storage_path / stored_filename are never exposed in API responses"""
    c = _create_client("fileclient22@example.com")
    project_id = _create_project(client, admin_headers, c.id)

    resp = client.post(
        f"/api/v1/projects/{project_id}/files",
        files={"file": ("doc.pdf", _pdf_bytes(), "application/pdf")},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "storage_path" not in body
    assert "stored_filename" not in body

    file_id = body["id"]
    resp = client.get(f"/api/v1/projects/{project_id}/files/{file_id}", headers=admin_headers)
    assert "storage_path" not in resp.json()
    assert "stored_filename" not in resp.json()

    resp = client.get(f"/api/v1/projects/{project_id}/files", headers=admin_headers)
    for item in resp.json():
        assert "storage_path" not in item
        assert "stored_filename" not in item


def test_existing_tests_continue_passing(client, admin_headers):
    """23. Existing project creation still works"""
    c = _create_client("fileclientfinal@example.com")
    resp = client.post(
        "/api/v1/projects",
        json={"client_id": c.id, "title": "Final Test", "description": "Test"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
