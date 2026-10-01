"""
Team members: self-registration, admin approval, project membership, and the
privacy wall that keeps a collaborator from ever seeing a client.

The privacy tests are the point of this file. They assert both halves:
the *keys* a team-facing response may not contain, and the absence of the
client's actual name from the raw response text -- so a future field that
smuggles client identity through under a different name still fails.
"""

import pytest

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.user import ApprovalStatus, Role
from app.schemas.user import UserCreate
from app.services import email_service
from tests.conftest import TestingSessionLocal

# Distinctive enough that finding it in a response body cannot be a coincidence.
CLIENT_NAME = "Zebulon Quailsworth"
CLIENT_EMAIL = "zebulon.quailsworth@example.com"


@pytest.fixture
def sent_emails(monkeypatch):
    captured: list[dict] = []

    def _fake_send_email(to_email, to_name, subject, html_content, text_content=None):
        captured.append({"to_email": to_email, "subject": subject, "html": html_content})
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send_email)
    return captured


def _make_user(
    email: str,
    role: Role = Role.CLIENT,
    full_name: str = "Team Person",
    approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password="password123"),
            role=role,
            approval_status=approval_status,
        )
    finally:
        db.close()


def _auth(user) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _by_email(email: str):
    db = TestingSessionLocal()
    try:
        return user_crud.get_by_email(db, email)
    finally:
        db.close()


def _register_team_member(client, email="intern@example.com", name="Ada Intern"):
    return client.post(
        "/api/v1/auth/register-team-member",
        json={"full_name": name, "email": email, "password": "password123"},
    )


def _make_project(client, admin_headers, *, title="Internal Tool", budget="4500000.00"):
    """A project for a client with a very distinctive name and a real budget."""
    c = _make_user(CLIENT_EMAIL, full_name=CLIENT_NAME)
    project = client.post(
        "/api/v1/projects",
        json={
            "client_id": c.id,
            "title": title,
            "description": "Build the internal tool.",
            "budget": budget,
        },
        headers=admin_headers,
    ).json()
    return c, project


def _assign(client, admin_headers, project_id, user_id, project_role="PROGRAMMER"):
    return client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": user_id, "project_role": project_role},
        headers=admin_headers,
    )


def _approved_team_member(client, admin_headers, email="dev@example.com", name="Dev Person"):
    _register_team_member(client, email, name)
    user = _by_email(email)
    client.patch(f"/api/v1/admin/team-members/{user.id}/approve", headers=admin_headers)
    return _by_email(email)


# --- self-registration ------------------------------------------------------


def test_self_registration_creates_a_pending_team_member(client, sent_emails):
    resp = _register_team_member(client)
    assert resp.status_code == 201
    assert "pending" in resp.json()["detail"].lower()

    user = _by_email("intern@example.com")
    assert user is not None
    assert user.role == Role.TEAM_MEMBER
    assert user.approval_status == ApprovalStatus.PENDING
    assert user.is_active is True


def test_registration_notifies_and_emails_admins(client, admin_headers, sent_emails):
    _register_team_member(client, name="Ada Intern")

    admin = _by_email("admin@example.com")
    notes = client.get("/api/v1/notifications", headers=_auth(admin)).json()
    registered = [n for n in notes if n["type"] == "TEAM_MEMBER_REGISTERED"]
    assert len(registered) == 1
    assert "Ada Intern" in registered[0]["message"]
    assert "intern@example.com" in registered[0]["message"]
    assert registered[0]["related_type"] == "team_member"

    assert [e["to_email"] for e in sent_emails] == ["admin@example.com"]
    assert "Ada Intern" in sent_emails[0]["subject"]


def test_staff_are_not_notified_of_registrations(client, staff_headers, sent_emails):
    """Approval is an admin action, so staff would only get noise."""
    _register_team_member(client)

    staff = _by_email("staff@example.com")
    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(staff)).json()]
    assert "TEAM_MEMBER_REGISTERED" not in types


def test_registration_cannot_claim_a_role_or_self_approve(client, sent_emails):
    """Extra fields in the body are ignored -- the endpoint sets both itself."""
    resp = client.post(
        "/api/v1/auth/register-team-member",
        json={
            "full_name": "Sneaky Person",
            "email": "sneaky@example.com",
            "password": "password123",
            "role": "ADMIN",
            "approval_status": "APPROVED",
        },
    )
    assert resp.status_code == 201

    user = _by_email("sneaky@example.com")
    assert user.role == Role.TEAM_MEMBER
    assert user.approval_status == ApprovalStatus.PENDING


def test_registration_enforces_the_password_minimum(client):
    resp = client.post(
        "/api/v1/auth/register-team-member",
        json={"full_name": "Short Pass", "email": "short@example.com", "password": "1234567"},
    )
    assert resp.status_code == 422
    assert _by_email("short@example.com") is None


def test_duplicate_registration_does_not_reveal_the_account(client, sent_emails):
    """Same response as a fresh registration -- no enumeration oracle."""
    existing = _make_user("taken@example.com", full_name="Already Here")
    first = existing.id

    resp = _register_team_member(client, "taken@example.com")
    assert resp.status_code == 201
    assert "pending" in resp.json()["detail"].lower()

    # Nothing was created and the existing account was not touched.
    still = _by_email("taken@example.com")
    assert still.id == first
    assert still.role == Role.CLIENT
    assert still.approval_status == ApprovalStatus.APPROVED


def test_plain_register_still_creates_an_approved_client(client):
    """The pre-existing /auth/register is unchanged."""
    resp = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Normal Client", "email": "normal@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "CLIENT"
    assert body["approval_status"] == "APPROVED"


# --- the approval gate ------------------------------------------------------


def test_pending_user_can_log_in(client, sent_emails):
    _register_team_member(client)
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "intern@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_pending_user_can_read_their_own_account(client, sent_emails):
    """/auth/me stays open so the frontend can show the awaiting-approval screen."""
    _register_team_member(client)
    headers = _auth(_by_email("intern@example.com"))

    for path in ("/api/v1/auth/me", "/api/v1/users/me"):
        resp = client.get(path, headers=headers)
        assert resp.status_code == 200, path
        assert resp.json()["approval_status"] == "PENDING"


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/v1/team/projects"),
        ("get", "/api/v1/team/projects/1"),
        ("get", "/api/v1/notifications"),
        ("get", "/api/v1/projects"),
        ("get", "/api/v1/invoices"),
        ("get", "/api/v1/admin/dashboard"),
        ("get", "/api/v1/client/dashboard"),
        ("get", "/api/v1/quote-requests"),
        ("get", "/api/v1/users"),
    ],
)
def test_pending_user_is_locked_out_of_everything(client, sent_emails, method, path):
    _register_team_member(client)
    headers = _auth(_by_email("intern@example.com"))

    resp = getattr(client, method)(path, headers=headers)
    assert resp.status_code == 403, f"{path} -> {resp.status_code}"
    assert "pending approval" in resp.json()["detail"].lower()


def test_rejected_user_is_locked_out_with_its_own_message(client, admin_headers, sent_emails):
    _register_team_member(client)
    user = _by_email("intern@example.com")
    client.patch(f"/api/v1/admin/team-members/{user.id}/reject", headers=admin_headers)

    resp = client.get("/api/v1/team/projects", headers=_auth(user))
    assert resp.status_code == 403
    detail = resp.json()["detail"].lower()
    assert "not approved" in detail
    assert "pending" not in detail


def test_existing_accounts_are_approved_and_unaffected(client, admin_headers, staff_headers, client_headers):
    """
    The gate must be a no-op for every account that predates it.

    The conftest fixtures create users exactly the way the app always has; if
    the default were anything but APPROVED, all three of these would 403.
    """
    assert client.get("/api/v1/admin/dashboard", headers=admin_headers).status_code == 200
    assert client.get("/api/v1/projects", headers=staff_headers).status_code == 200
    assert client.get("/api/v1/client/dashboard", headers=client_headers).status_code == 200

    for email in ("admin@example.com", "staff@example.com", "client@example.com"):
        assert _by_email(email).approval_status == ApprovalStatus.APPROVED, email


# --- admin approval ---------------------------------------------------------


def test_admin_lists_pending_registrations(client, admin_headers, sent_emails):
    _register_team_member(client, "one@example.com", "One Person")
    _register_team_member(client, "two@example.com", "Two Person")
    approved = _approved_team_member(client, admin_headers, "three@example.com", "Three Person")

    resp = client.get("/api/v1/admin/team-members/pending", headers=admin_headers)
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert emails == {"one@example.com", "two@example.com"}
    assert approved.email not in emails


def test_approval_opens_access_and_emails_the_member(client, admin_headers, sent_emails):
    _register_team_member(client)
    user = _by_email("intern@example.com")
    assert client.get("/api/v1/team/projects", headers=_auth(user)).status_code == 403
    sent_emails.clear()

    resp = client.patch(f"/api/v1/admin/team-members/{user.id}/approve", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["approval_status"] == "APPROVED"

    # They can reach their own area now.
    assert client.get("/api/v1/team/projects", headers=_auth(user)).status_code == 200

    types = [n["type"] for n in client.get("/api/v1/notifications", headers=_auth(user)).json()]
    assert "TEAM_MEMBER_APPROVED" in types
    assert [e["to_email"] for e in sent_emails] == ["intern@example.com"]
    assert "approved" in sent_emails[0]["subject"].lower()


def test_re_approving_does_not_renotify(client, admin_headers, sent_emails):
    user = _approved_team_member(client, admin_headers)
    sent_emails.clear()

    client.patch(f"/api/v1/admin/team-members/{user.id}/approve", headers=admin_headers)

    assert sent_emails == []
    approvals = [
        n
        for n in client.get("/api/v1/notifications", headers=_auth(user)).json()
        if n["type"] == "TEAM_MEMBER_APPROVED"
    ]
    assert len(approvals) == 1


def test_rejection_emails_the_member_with_the_reason(client, admin_headers, sent_emails):
    _register_team_member(client)
    user = _by_email("intern@example.com")
    sent_emails.clear()

    resp = client.patch(
        f"/api/v1/admin/team-members/{user.id}/reject",
        json={"reason": "No current openings"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["approval_status"] == "REJECTED"
    assert [e["to_email"] for e in sent_emails] == ["intern@example.com"]
    assert "No current openings" in sent_emails[0]["html"]


def test_approval_endpoints_cannot_touch_other_roles(client, admin_headers, sent_emails):
    """
    The hard foot-gun: these must not be a way to flip the approval flag on a
    CLIENT, STAFF or ADMIN account.
    """
    a_client = _make_user("plainclient@example.com")
    staff = _make_user("plainstaff@example.com", role=Role.STAFF)

    for user in (a_client, staff):
        for action in ("approve", "reject"):
            resp = client.patch(
                f"/api/v1/admin/team-members/{user.id}/{action}", headers=admin_headers
            )
            assert resp.status_code == 404, f"{user.email} {action}"

    assert _by_email("plainclient@example.com").approval_status == ApprovalStatus.APPROVED
    assert _by_email("plainstaff@example.com").approval_status == ApprovalStatus.APPROVED


def test_staff_cannot_approve_team_members(client, admin_headers, staff_headers, sent_emails):
    _register_team_member(client)
    user = _by_email("intern@example.com")

    assert client.get("/api/v1/admin/team-members/pending", headers=staff_headers).status_code == 403
    assert (
        client.patch(
            f"/api/v1/admin/team-members/{user.id}/approve", headers=staff_headers
        ).status_code
        == 403
    )
    assert _by_email("intern@example.com").approval_status == ApprovalStatus.PENDING


def test_dashboard_counts_pending_approvals(client, admin_headers, sent_emails):
    before = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert before["team"] == {"pending_approvals": 0, "approved_members": 0}

    _register_team_member(client, "p1@example.com")
    _register_team_member(client, "p2@example.com")
    _approved_team_member(client, admin_headers, "a1@example.com")

    after = client.get("/api/v1/admin/dashboard", headers=admin_headers).json()
    assert after["team"] == {"pending_approvals": 2, "approved_members": 1}


# --- project membership -----------------------------------------------------


def test_assigning_a_member_notifies_and_emails_them(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)
    sent_emails.clear()

    resp = _assign(client, admin_headers, project["id"], member.id, "TEAM_LEAD")
    assert resp.status_code == 201
    body = resp.json()
    assert body["user_id"] == member.id
    assert body["project_role"] == "TEAM_LEAD"
    assert body["user_full_name"] == "Dev Person"
    assert body["is_active"] is True

    notes = client.get("/api/v1/notifications", headers=_auth(member)).json()
    assignment = [n for n in notes if n["type"] == "PROJECT_ASSIGNMENT"]
    assert len(assignment) == 1
    assert assignment[0]["related_type"] == "project"
    assert assignment[0]["related_id"] == project["id"]
    assert "Team Lead" in assignment[0]["message"]

    assert [e["to_email"] for e in sent_emails] == [member.email]


def test_the_assignment_notification_leaks_no_client_or_money(
    client, admin_headers, sent_emails
):
    """An email is a disclosure too -- the wall applies to it as well."""
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers, budget="4500000.00")
    sent_emails.clear()

    _assign(client, admin_headers, project["id"], member.id)

    notes = client.get("/api/v1/notifications", headers=_auth(member)).json()
    blob = str(notes) + str(sent_emails)
    assert CLIENT_NAME not in blob
    assert CLIENT_EMAIL not in blob
    assert "4500000" not in blob


def test_a_project_role_is_unique_per_project_and_reassignment_reactivates(
    client, admin_headers, sent_emails
):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)

    first = _assign(client, admin_headers, project["id"], member.id, "PROGRAMMER").json()
    client.delete(
        f"/api/v1/projects/{project['id']}/members/{first['id']}", headers=admin_headers
    )

    again = _assign(client, admin_headers, project["id"], member.id, "TESTER").json()
    # Same row, reactivated with the new role -- not a duplicate.
    assert again["id"] == first["id"]
    assert again["project_role"] == "TESTER"
    assert again["is_active"] is True

    members = client.get(
        f"/api/v1/projects/{project['id']}/members?include_inactive=true",
        headers=admin_headers,
    ).json()
    assert len(members) == 1


def test_changing_an_active_members_role_does_not_renotify(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)
    _assign(client, admin_headers, project["id"], member.id, "PROGRAMMER")
    sent_emails.clear()

    _assign(client, admin_headers, project["id"], member.id, "DESIGNER")

    assert sent_emails == []
    assignments = [
        n
        for n in client.get("/api/v1/notifications", headers=_auth(member)).json()
        if n["type"] == "PROJECT_ASSIGNMENT"
    ]
    assert len(assignments) == 1


def test_patch_changes_a_members_role(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)
    assigned = _assign(client, admin_headers, project["id"], member.id).json()

    resp = client.patch(
        f"/api/v1/projects/{project['id']}/members/{assigned['id']}",
        json={"project_role": "RESEARCHER"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["project_role"] == "RESEARCHER"

    detail = client.get(f"/api/v1/team/projects/{project['id']}", headers=_auth(member)).json()
    assert detail["my_role"] == "RESEARCHER"


def test_a_client_cannot_be_assigned_to_a_project(client, admin_headers, sent_emails):
    a_client, project = _make_project(client, admin_headers)
    resp = _assign(client, admin_headers, project["id"], a_client.id)
    assert resp.status_code == 422


def test_a_pending_team_member_cannot_be_assigned(client, admin_headers, sent_emails):
    """Work assigned to an account that can't log in is a dead notification."""
    _register_team_member(client)
    pending = _by_email("intern@example.com")
    _, project = _make_project(client, admin_headers)

    resp = _assign(client, admin_headers, project["id"], pending.id)
    assert resp.status_code == 422


def test_staff_can_be_assigned_to_a_project(client, admin_headers, staff_headers, sent_emails):
    staff = _by_email("staff@example.com")
    _, project = _make_project(client, admin_headers)

    resp = _assign(client, admin_headers, project["id"], staff.id, "TEAM_LEAD")
    assert resp.status_code == 201


def test_members_endpoints_are_closed_to_clients_and_team_members(
    client, admin_headers, client_headers, sent_emails
):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)

    for headers in (client_headers, _auth(member)):
        assert (
            client.get(f"/api/v1/projects/{project['id']}/members", headers=headers).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/v1/projects/{project['id']}/members",
                json={"user_id": member.id, "project_role": "TESTER"},
                headers=headers,
            ).status_code
            == 403
        )


# --- the team member's own view --------------------------------------------


def test_a_member_sees_only_the_projects_they_are_on(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, mine = _make_project(client, admin_headers, title="Assigned To Me")
    theirs = client.post(
        "/api/v1/projects",
        json={
            "client_id": _make_user("other@example.com", full_name="Other Client").id,
            "title": "Somebody Else's Project",
            "description": "d",
        },
        headers=admin_headers,
    ).json()
    _assign(client, admin_headers, mine["id"], member.id)

    listed = client.get("/api/v1/team/projects", headers=_auth(member)).json()
    assert [p["title"] for p in listed] == ["Assigned To Me"]

    # And the other one is simply not there -- 404, not 403.
    assert client.get(f"/api/v1/team/projects/{theirs['id']}", headers=_auth(member)).status_code == 404


def test_removing_a_member_takes_the_project_away(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)
    assigned = _assign(client, admin_headers, project["id"], member.id).json()
    assert len(client.get("/api/v1/team/projects", headers=_auth(member)).json()) == 1

    client.delete(
        f"/api/v1/projects/{project['id']}/members/{assigned['id']}", headers=admin_headers
    )

    assert client.get("/api/v1/team/projects", headers=_auth(member)).json() == []
    assert (
        client.get(f"/api/v1/team/projects/{project['id']}", headers=_auth(member)).status_code
        == 404
    )


def test_deactivating_a_project_takes_it_away_too(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)
    _assign(client, admin_headers, project["id"], member.id)

    client.delete(f"/api/v1/projects/{project['id']}", headers=admin_headers)

    assert client.get("/api/v1/team/projects", headers=_auth(member)).json() == []


def test_the_detail_view_carries_the_technical_work(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers)
    _assign(client, admin_headers, project["id"], member.id, "TESTER")
    client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Ship the API", "description": "All endpoints live"},
        headers=admin_headers,
    )

    body = client.get(f"/api/v1/team/projects/{project['id']}", headers=_auth(member)).json()
    assert body["title"] == "Internal Tool"
    assert body["description"] == "Build the internal tool."
    assert body["my_role"] == "TESTER"
    assert [m["title"] for m in body["milestones"]] == ["Ship the API"]
    assert body["files"] == []


def test_the_team_endpoints_are_closed_to_everyone_else(
    client, admin_headers, staff_headers, client_headers
):
    for headers in (admin_headers, staff_headers, client_headers):
        assert client.get("/api/v1/team/projects", headers=headers).status_code == 403


# --- THE PRIVACY WALL -------------------------------------------------------

# Every key that would identify the client or expose money. `my_role` is the
# only field on the team schemas that isn't straight off the project row.
FORBIDDEN_KEYS = (
    "client_id",
    "client",
    "client_name",
    "client_email",
    "budget",
    "amount_paid",
    "quote_request_id",
    "invoice",
    "invoices",
    "uploaded_by",
)


def _assert_no_client_data(payload, raw_text: str, label: str):
    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                assert key not in FORBIDDEN_KEYS, f"{label}: forbidden key {path}.{key}"
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    walk(payload, label)
    # The second half: not just the known key names, but the client's actual
    # identity, however it might have travelled.
    assert CLIENT_NAME not in raw_text, f"{label}: client name present in the body"
    assert CLIENT_EMAIL not in raw_text, f"{label}: client email present in the body"
    assert "4500000" not in raw_text, f"{label}: budget present in the body"


def test_team_project_list_leaks_nothing_about_the_client(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    _, project = _make_project(client, admin_headers, budget="4500000.00")
    _assign(client, admin_headers, project["id"], member.id)

    resp = client.get("/api/v1/team/projects", headers=_auth(member))
    assert resp.status_code == 200
    _assert_no_client_data(resp.json(), resp.text, "/team/projects")

    # Sanity: the useful fields really are there, so the test isn't passing
    # because the response is empty.
    assert resp.json()[0]["title"] == "Internal Tool"
    assert resp.json()[0]["my_role"] == "PROGRAMMER"


def test_team_project_detail_leaks_nothing_about_the_client(client, admin_headers, sent_emails):
    member = _approved_team_member(client, admin_headers)
    a_client, project = _make_project(client, admin_headers, budget="4500000.00")
    _assign(client, admin_headers, project["id"], member.id)
    client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Phase one", "description": "Groundwork"},
        headers=admin_headers,
    )

    resp = client.get(f"/api/v1/team/projects/{project['id']}", headers=_auth(member))
    assert resp.status_code == 200
    _assert_no_client_data(resp.json(), resp.text, "/team/projects/{id}")

    assert resp.json()["title"] == "Internal Tool"
    assert len(resp.json()["milestones"]) == 1
    # The project really does have the data that must not appear -- otherwise
    # this whole test would be vacuous.
    staff_view = client.get(f"/api/v1/projects/{project['id']}", headers=admin_headers).json()
    assert staff_view["client_id"] == a_client.id
    assert staff_view["budget"] == "4500000.00"


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/v1/invoices"),
        ("get", "/api/v1/client/dashboard"),
        ("get", "/api/v1/client/projects"),
        ("get", "/api/v1/client/invoices"),
        ("get", "/api/v1/client/quotes"),
        ("get", "/api/v1/admin/dashboard"),
        ("get", "/api/v1/admin/users"),
        ("get", "/api/v1/admin/team-members/pending"),
        ("get", "/api/v1/quote-requests"),
        ("get", "/api/v1/projects"),
        ("get", "/api/v1/projects/1"),
        ("get", "/api/v1/projects/1/milestones"),
        ("get", "/api/v1/projects/1/files"),
        ("get", "/api/v1/projects/1/members"),
        ("get", "/api/v1/users"),
        ("get", "/api/v1/tickets"),
        ("get", "/api/v1/hosting/accounts"),
        ("get", "/api/v1/domains"),
        ("get", "/api/v1/settings"),
    ],
)
def test_a_team_member_is_forbidden_everywhere_else(client, admin_headers, method, path):
    member = _approved_team_member(client, admin_headers)
    resp = getattr(client, method)(path, headers=_auth(member))
    assert resp.status_code == 403, f"{path} -> {resp.status_code}"


def test_no_route_outside_team_answers_a_team_member(client, admin_headers, sent_emails):
    """
    The sweep that catches what a hand-written list can't: walk every GET in the
    OpenAPI schema and assert a team member is never served one, except on the
    surface they are meant to have.

    This is the regression net for the privacy wall. A new endpoint added later
    that reads through `ActiveUser` instead of `NonTeamUser` fails here rather
    than in production.
    """
    from app.main import app

    member = _approved_team_member(client, admin_headers)
    headers = _auth(member)

    # Everything here is either the member's own data or already public to
    # anonymous visitors, and none of it carries client or billing information.
    # Adding to this list is a deliberate decision, which is the point.
    allowed_prefixes = (
        "/api/v1/team/",            # their own, privacy-walled surface
        "/api/v1/notifications",    # their own bell
        "/api/v1/auth/me",          # their own account
        "/api/v1/users/me",         # their own account
        "/api/v1/services",         # public catalogue, no client data
        "/api/v1/settings/public",  # public company info
        "/api/v1/hosting/plans",    # public pricing page -- marketing copy only
        "/health",                  # liveness probe, no body to speak of
    )

    served: list[str] = []
    for path, operations in app.openapi()["paths"].items():
        if "get" not in operations:
            continue
        if path.startswith(allowed_prefixes):
            continue
        # Concrete ids: the point is the authorization outcome, and a 404 is
        # just as much a "not served" as a 403.
        concrete = path
        for param in ("{project_id}", "{user_id}", "{file_id}", "{milestone_id}",
                      "{invoice_id}", "{ticket_id}", "{quote_id}", "{member_id}",
                      "{notification_id}", "{service_id}", "{account_id}",
                      "{domain_id}", "{plan_id}", "{payment_id}", "{id}"):
            concrete = concrete.replace(param, "1")
        if "{" in concrete:
            continue  # an unmapped param name -- surfaced by the assert below

        resp = client.get(concrete, headers=headers)
        if resp.status_code == 200:
            served.append(f"{concrete} -> 200")

    assert served == [], "a team member was served data outside /team: " + ", ".join(served)
