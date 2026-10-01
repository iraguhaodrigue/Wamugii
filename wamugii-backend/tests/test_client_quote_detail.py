"""
Client-facing quote detail.

This closes the gap the notifications module left: QUOTE_STATUS_CHANGED notifies
a client, but there was no client-facing quote route to click through to.
"""

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate
from tests.conftest import TestingSessionLocal


def _make_client(email: str, full_name: str = "Quote Client"):
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


def _submit_quote(client, email: str, title: str = "New website", **overrides) -> dict:
    payload = {
        "full_name": "Quote Client",
        "email": email,
        "phone": "0700000000",
        "project_title": title,
        "project_description": "Please build us a marketing site.",
        "budget_range": "RWF 1,000,000 – 3,000,000",
        "preferred_deadline": "Within 2 months",
    }
    payload.update(overrides)
    return client.post("/api/v1/quote-requests", json=payload).json()


def test_client_can_view_their_own_quote(client):
    c = _make_client("quote_own@example.com")
    quote = _submit_quote(client, "quote_own@example.com")

    resp = client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(c))
    assert resp.status_code == 200
    body = resp.json()
    assert body["project_title"] == "New website"
    assert body["project_description"] == "Please build us a marketing site."
    assert body["budget_range"] == "RWF 1,000,000 – 3,000,000"
    assert body["preferred_deadline"] == "Within 2 months"
    assert body["status"] == "NEW"


def test_admin_notes_never_reach_the_client(client, admin_headers):
    c = _make_client("quote_notes@example.com")
    quote = _submit_quote(client, "quote_notes@example.com")

    SECRET = "Lowball budget — quote high. INTERNAL"
    client.patch(
        f"/api/v1/quote-requests/{quote['id']}",
        json={"admin_notes": SECRET, "status": "REVIEWING"},
        headers=admin_headers,
    )

    resp = client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(c))
    assert resp.status_code == 200
    assert "admin_notes" not in resp.json()
    assert SECRET not in resp.text
    # The status change itself is visible — that's the point of the page.
    assert resp.json()["status"] == "REVIEWING"


def test_cross_client_quote_returns_404(client):
    c1 = _make_client("quote_a@example.com")
    c2 = _make_client("quote_b@example.com")
    theirs = _submit_quote(client, "quote_a@example.com")

    assert client.get(f"/api/v1/client/quotes/{theirs['id']}", headers=_auth(c2)).status_code == 404
    # ...and the owner still can.
    assert client.get(f"/api/v1/client/quotes/{theirs['id']}", headers=_auth(c1)).status_code == 200


def test_unknown_quote_returns_404(client):
    c = _make_client("quote_missing@example.com")
    assert client.get("/api/v1/client/quotes/999999", headers=_auth(c)).status_code == 404


def test_quote_detail_requires_a_client_login(client, admin_headers, staff_headers):
    c = _make_client("quote_roles@example.com")
    quote = _submit_quote(client, "quote_roles@example.com")

    assert client.get(f"/api/v1/client/quotes/{quote['id']}").status_code == 401
    assert client.get(f"/api/v1/client/quotes/{quote['id']}", headers=admin_headers).status_code == 403
    assert client.get(f"/api/v1/client/quotes/{quote['id']}", headers=staff_headers).status_code == 403


def test_service_name_is_resolved(client, admin_headers):
    c = _make_client("quote_service@example.com")
    service = client.post(
        "/api/v1/services", json={"name": "Web Design & Development"}, headers=admin_headers
    ).json()
    quote = _submit_quote(client, "quote_service@example.com", service_id=service["id"])

    body = client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(c)).json()
    assert body["service_id"] == service["id"]
    # Resolved so the page shows a name rather than an id.
    assert body["service_name"] == "Web Design & Development"


def test_converted_project_is_linked(client, admin_headers):
    """Once a quote becomes a project, the client can click through to it."""
    c = _make_client("quote_converted@example.com")
    quote = _submit_quote(client, "quote_converted@example.com")

    before = client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(c)).json()
    assert before["converted_project_id"] is None

    client.patch(
        f"/api/v1/quote-requests/{quote['id']}", json={"status": "ACCEPTED"}, headers=admin_headers
    )
    project = client.post(
        f"/api/v1/quote-requests/{quote['id']}/create-project?client_id={c.id}",
        headers=admin_headers,
    ).json()

    after = client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(c)).json()
    assert after["converted_project_id"] == project["id"]
    # And that project really is reachable by this client.
    assert client.get(
        f"/api/v1/client/projects/{project['id']}", headers=_auth(c)
    ).status_code == 200


def test_quote_detail_matches_the_list(client):
    """The detail endpoint covers the same quotes the list shows."""
    c = _make_client("quote_list@example.com")
    quote = _submit_quote(client, "quote_list@example.com")

    listed = client.get("/api/v1/client/quotes", headers=_auth(c)).json()
    assert [q["id"] for q in listed] == [quote["id"]]
    assert client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(c)).status_code == 200
