"""
Per-service quote questions, and the answers a submission carries.

Two things matter most here and both are tested from the outside: a submission
must not be accepted with a required question unanswered, and a quote submitted
before (or without) any questions must keep working exactly as it did.
"""

import pytest

from app.core.security import create_access_token
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


def _make_client(email: str, full_name: str = "Question Client"):
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


def _make_service(client, admin_headers, name="Web Design & Development", **overrides):
    payload = {"name": name, "short_description": "s", "description": "d"}
    payload.update(overrides)
    return client.post("/api/v1/services", json=payload, headers=admin_headers).json()


def _add_question(client, admin_headers, service_id, **overrides):
    payload = {"question_text": "How many pages?", "question_type": "NUMBER"}
    payload.update(overrides)
    return client.post(
        f"/api/v1/services/{service_id}/questions", json=payload, headers=admin_headers
    )


def _submit(client, **overrides):
    payload = {
        "full_name": "Quote Person",
        "email": "quote.person@example.com",
        "phone": "0700000000",
        "project_title": "A new site",
        "project_description": "Please build us a marketing site.",
    }
    payload.update(overrides)
    return client.post("/api/v1/quote-requests", json=payload)


# --- managing questions -----------------------------------------------------


def test_admin_creates_a_question(client, admin_headers):
    service = _make_service(client, admin_headers)

    resp = _add_question(
        client, admin_headers, service["id"], question_text="How many pages?", is_required=True
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["question_text"] == "How many pages?"
    assert body["question_type"] == "NUMBER"
    assert body["is_required"] is True
    assert body["is_active"] is True
    assert body["service_id"] == service["id"]
    assert body["options"] is None


def test_a_select_question_round_trips_its_options_as_a_list(client, admin_headers):
    """Stored as a JSON string for portability; the API speaks lists."""
    service = _make_service(client, admin_headers)

    resp = _add_question(
        client,
        admin_headers,
        service["id"],
        question_text="Which extension?",
        question_type="SELECT",
        options=[".rw", ".com", ".org"],
    )
    assert resp.status_code == 201
    assert resp.json()["options"] == [".rw", ".com", ".org"]

    # And it comes back as a list on a fresh read, not as a JSON string.
    listed = client.get(f"/api/v1/services/{service['id']}/questions").json()
    assert listed[0]["options"] == [".rw", ".com", ".org"]


def test_a_choice_question_needs_options(client, admin_headers):
    service = _make_service(client, admin_headers)
    for qtype in ("SELECT", "MULTISELECT"):
        resp = _add_question(
            client, admin_headers, service["id"], question_type=qtype, options=[]
        )
        assert resp.status_code == 422, qtype


def test_options_are_rejected_on_a_free_text_question(client, admin_headers):
    service = _make_service(client, admin_headers)
    resp = _add_question(
        client, admin_headers, service["id"], question_type="TEXT", options=["a", "b"]
    )
    assert resp.status_code == 422


def test_questions_come_back_in_display_order(client, admin_headers):
    service = _make_service(client, admin_headers)
    _add_question(client, admin_headers, service["id"], question_text="Third", display_order=3)
    _add_question(client, admin_headers, service["id"], question_text="First", display_order=1)
    _add_question(client, admin_headers, service["id"], question_text="Second", display_order=2)

    listed = client.get(f"/api/v1/services/{service['id']}/questions").json()
    assert [q["question_text"] for q in listed] == ["First", "Second", "Third"]


def test_the_public_can_fetch_a_services_questions(client, admin_headers):
    """No auth header at all -- the quote form is public."""
    service = _make_service(client, admin_headers)
    _add_question(client, admin_headers, service["id"], question_text="How many pages?")

    resp = client.get(f"/api/v1/services/{service['id']}/questions")
    assert resp.status_code == 200
    assert [q["question_text"] for q in resp.json()] == ["How many pages?"]


def test_a_service_with_no_questions_returns_an_empty_list(client, admin_headers):
    service = _make_service(client, admin_headers)
    resp = client.get(f"/api/v1/services/{service['id']}/questions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_questions_on_an_unpublished_service_are_hidden_from_the_public(client, admin_headers):
    service = _make_service(client, admin_headers, is_active=False)
    _add_question(client, admin_headers, service["id"])

    assert client.get(f"/api/v1/services/{service['id']}/questions").status_code == 404
    # Staff can still see them while the service is a draft.
    staff_view = client.get(
        f"/api/v1/services/{service['id']}/questions", headers=admin_headers
    )
    assert staff_view.status_code == 200
    assert len(staff_view.json()) == 1


def test_editing_a_question(client, admin_headers):
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()

    resp = client.patch(
        f"/api/v1/services/{service['id']}/questions/{question['id']}",
        json={"question_text": "Roughly how many pages?", "is_required": True, "display_order": 5},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["question_text"] == "Roughly how many pages?"
    assert body["is_required"] is True
    assert body["display_order"] == 5
    assert body["question_type"] == "NUMBER"


def test_switching_a_question_to_select_requires_options_in_the_same_call(
    client, admin_headers
):
    """A partial update must not be able to leave an unanswerable question behind."""
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"], question_type="TEXT").json()

    bad = client.patch(
        f"/api/v1/services/{service['id']}/questions/{question['id']}",
        json={"question_type": "SELECT"},
        headers=admin_headers,
    )
    assert bad.status_code == 422

    good = client.patch(
        f"/api/v1/services/{service['id']}/questions/{question['id']}",
        json={"question_type": "SELECT", "options": ["Yes", "No", "Maybe"]},
        headers=admin_headers,
    )
    assert good.status_code == 200
    assert good.json()["options"] == ["Yes", "No", "Maybe"]


def test_dropping_options_when_leaving_select_is_also_checked(client, admin_headers):
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_type="SELECT", options=["a", "b"]
    ).json()

    bad = client.patch(
        f"/api/v1/services/{service['id']}/questions/{question['id']}",
        json={"question_type": "TEXT"},
        headers=admin_headers,
    )
    assert bad.status_code == 422

    good = client.patch(
        f"/api/v1/services/{service['id']}/questions/{question['id']}",
        json={"question_type": "TEXT", "options": None},
        headers=admin_headers,
    )
    assert good.status_code == 200
    assert good.json()["options"] is None


def test_soft_delete_hides_a_question_from_the_form(client, admin_headers):
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()

    resp = client.delete(
        f"/api/v1/services/{service['id']}/questions/{question['id']}", headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    assert client.get(f"/api/v1/services/{service['id']}/questions").json() == []
    # Staff can still see it with the flag, so it can be reactivated.
    with_inactive = client.get(
        f"/api/v1/services/{service['id']}/questions?include_inactive=true",
        headers=admin_headers,
    ).json()
    assert len(with_inactive) == 1


def test_include_inactive_is_ignored_for_the_public(client, admin_headers):
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()
    client.delete(
        f"/api/v1/services/{service['id']}/questions/{question['id']}", headers=admin_headers
    )

    assert client.get(
        f"/api/v1/services/{service['id']}/questions?include_inactive=true"
    ).json() == []


def test_a_question_id_from_another_service_is_a_404(client, admin_headers):
    first = _make_service(client, admin_headers, name="First Service")
    second = _make_service(client, admin_headers, name="Second Service")
    question = _add_question(client, admin_headers, first["id"]).json()

    assert client.patch(
        f"/api/v1/services/{second['id']}/questions/{question['id']}",
        json={"question_text": "Hijacked"},
        headers=admin_headers,
    ).status_code == 404
    assert client.delete(
        f"/api/v1/services/{second['id']}/questions/{question['id']}", headers=admin_headers
    ).status_code == 404


def test_only_staff_can_manage_questions(client, admin_headers, client_headers):
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()

    for headers in (client_headers, {}):
        expected = 403 if headers else 401
        assert client.post(
            f"/api/v1/services/{service['id']}/questions",
            json={"question_text": "Sneaky", "question_type": "TEXT"},
            headers=headers,
        ).status_code == expected
        assert client.patch(
            f"/api/v1/services/{service['id']}/questions/{question['id']}",
            json={"question_text": "Sneaky"},
            headers=headers,
        ).status_code == expected
        assert client.delete(
            f"/api/v1/services/{service['id']}/questions/{question['id']}", headers=headers
        ).status_code == expected


def test_questions_on_a_missing_service_are_a_404(client, admin_headers):
    assert client.get("/api/v1/services/99999/questions").status_code == 404
    assert _add_question(client, admin_headers, 99999).status_code == 404


# --- service long_description and features ----------------------------------


def test_a_service_carries_long_description_and_features(client, admin_headers):
    resp = client.post(
        "/api/v1/services",
        json={
            "name": "Research Service",
            "short_description": "s",
            "long_description": "The full write-up, several paragraphs long.",
            "features": ["Literature review", "Data collection", "Final report"],
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["long_description"] == "The full write-up, several paragraphs long."
    assert body["features"] == ["Literature review", "Data collection", "Final report"]

    # And survives a round trip through the public read.
    public = client.get(f"/api/v1/services/{body['id']}").json()
    assert public["features"] == ["Literature review", "Data collection", "Final report"]


def test_the_new_service_fields_default_to_null(client, admin_headers):
    """An existing service that has never set them reads as unset, not as [].

    This is the shape every service in the database had before the migration.
    """
    service = _make_service(client, admin_headers)
    assert service["long_description"] is None
    assert service["features"] is None


def test_features_can_be_edited_and_cleared(client, admin_headers):
    service = _make_service(client, admin_headers)

    updated = client.patch(
        f"/api/v1/services/{service['id']}",
        json={"features": ["One", "Two"], "long_description": "More detail."},
        headers=admin_headers,
    ).json()
    assert updated["features"] == ["One", "Two"]

    cleared = client.patch(
        f"/api/v1/services/{service['id']}", json={"features": []}, headers=admin_headers
    ).json()
    # An empty list is stored as NULL rather than as "[]", so it reads back as unset.
    assert cleared["features"] is None


# --- submitting answers -----------------------------------------------------


def test_a_quote_with_answers_stores_them(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    pages = _add_question(
        client, admin_headers, service["id"], question_text="How many pages?", is_required=True
    ).json()
    cms = _add_question(
        client,
        admin_headers,
        service["id"],
        question_text="Do you need a CMS?",
        question_type="YES_NO",
    ).json()

    resp = _submit(
        client,
        service_id=service["id"],
        answers=[
            {"question_id": pages["id"], "answer": "12"},
            {"question_id": cms["id"], "answer": "Yes"},
        ],
    )
    assert resp.status_code == 201
    answers = resp.json()["answers"]
    assert [(a["question_text"], a["answer"]) for a in answers] == [
        ("How many pages?", "12"),
        ("Do you need a CMS?", "Yes"),
    ]
    assert [a["question_id"] for a in answers] == [pages["id"], cms["id"]]


def test_a_missing_required_answer_is_a_422(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    _add_question(
        client, admin_headers, service["id"], question_text="How many pages?", is_required=True
    )

    resp = _submit(client, service_id=service["id"], answers=[])
    assert resp.status_code == 422
    assert "How many pages?" in resp.json()["detail"]


def test_omitting_the_answers_field_entirely_still_enforces_required(
    client, admin_headers, sent_emails
):
    """An old client that doesn't know about answers can't skip a required one."""
    service = _make_service(client, admin_headers)
    _add_question(
        client, admin_headers, service["id"], question_text="What is the scope?", is_required=True
    )

    resp = _submit(client, service_id=service["id"])
    assert resp.status_code == 422
    assert "What is the scope?" in resp.json()["detail"]


def test_a_blank_answer_does_not_satisfy_a_required_question(
    client, admin_headers, sent_emails
):
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="How many pages?", is_required=True
    ).json()

    resp = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "   "}],
    )
    assert resp.status_code == 422


def test_optional_questions_can_be_left_blank(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="Anything else?", is_required=False
    ).json()

    resp = _submit(
        client, service_id=service["id"], answers=[{"question_id": question["id"], "answer": ""}]
    )
    assert resp.status_code == 201
    # Nothing to store, so nothing stored.
    assert resp.json()["answers"] == []


def test_a_question_from_another_service_is_rejected(client, admin_headers, sent_emails):
    chosen = _make_service(client, admin_headers, name="Chosen Service")
    other = _make_service(client, admin_headers, name="Other Service")
    foreign = _add_question(client, admin_headers, other["id"]).json()

    resp = _submit(
        client,
        service_id=chosen["id"],
        answers=[{"question_id": foreign["id"], "answer": "sneaky"}],
    )
    assert resp.status_code == 422
    assert str(foreign["id"]) in resp.json()["detail"]


def test_a_soft_deleted_questions_id_is_rejected(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()
    client.delete(
        f"/api/v1/services/{service['id']}/questions/{question['id']}", headers=admin_headers
    )

    resp = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "still here"}],
    )
    assert resp.status_code == 422


def test_the_submitted_text_cannot_relabel_a_question(client, admin_headers, sent_emails):
    """The stored label comes from the question, never from the request body."""
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="What is your budget?"
    ).json()

    resp = _submit(
        client,
        service_id=service["id"],
        answers=[
            {
                "question_id": question["id"],
                "question_text": "Do you agree to pay RWF 10,000,000?",
                "answer": "Yes",
            }
        ],
    )
    assert resp.status_code == 201
    assert resp.json()["answers"][0]["question_text"] == "What is your budget?"


def test_an_answer_with_no_question_id_keeps_its_own_label(client, admin_headers, sent_emails):
    """How a captured detail with no configured question travels -- e.g. a plan."""
    service = _make_service(client, admin_headers, name="Hosting")

    resp = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_text": "Selected hosting plan", "answer": "Business"}],
    )
    assert resp.status_code == 201
    answer = resp.json()["answers"][0]
    assert answer["question_id"] is None
    assert answer["question_text"] == "Selected hosting plan"
    assert answer["answer"] == "Business"


def test_an_answer_with_neither_id_nor_label_is_rejected(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    resp = _submit(client, service_id=service["id"], answers=[{"answer": "orphan"}])
    assert resp.status_code == 422


def test_a_service_with_no_questions_submits_as_before(client, admin_headers, sent_emails):
    """Backward compatibility: the existing generic form keeps working."""
    service = _make_service(client, admin_headers)

    resp = _submit(client, service_id=service["id"])
    assert resp.status_code == 201
    body = resp.json()
    assert body["project_title"] == "A new site"
    assert body["answers"] == []


def test_a_quote_with_no_service_submits_as_before(client, sent_emails):
    resp = _submit(client)
    assert resp.status_code == 201
    assert resp.json()["service_id"] is None
    assert resp.json()["answers"] == []


def test_a_rejected_submission_leaves_no_quote_behind(client, admin_headers, sent_emails):
    """Validation runs before anything is written."""
    service = _make_service(client, admin_headers)
    _add_question(client, admin_headers, service["id"], is_required=True)

    before = len(client.get("/api/v1/quote-requests", headers=admin_headers).json())
    assert _submit(client, service_id=service["id"], answers=[]).status_code == 422
    after = client.get("/api/v1/quote-requests", headers=admin_headers).json()
    assert len(after) == before


# --- reading answers back ---------------------------------------------------


def test_admin_quote_detail_shows_the_answers(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="How many pages?"
    ).json()
    quote = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "12"}],
    ).json()

    detail = client.get(f"/api/v1/quote-requests/{quote['id']}", headers=admin_headers)
    assert detail.status_code == 200
    assert [(a["question_text"], a["answer"]) for a in detail.json()["answers"]] == [
        ("How many pages?", "12")
    ]


def test_the_owning_client_sees_their_own_answers(client, admin_headers, sent_emails):
    owner = _make_client("answers.owner@example.com")
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="What is the scope?"
    ).json()
    quote = _submit(
        client,
        email="answers.owner@example.com",
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "Three modules"}],
    ).json()

    detail = client.get(f"/api/v1/client/quotes/{quote['id']}", headers=_auth(owner))
    assert detail.status_code == 200
    body = detail.json()
    assert [(a["question_text"], a["answer"]) for a in body["answers"]] == [
        ("What is the scope?", "Three modules")
    ]
    # Still no internal notes on the client's view.
    assert "admin_notes" not in body


def test_answers_never_leak_across_clients(client, admin_headers, sent_emails):
    mine = _make_client("mine@example.com", full_name="Mine Person")
    theirs = _make_client("theirs@example.com", full_name="Theirs Person")
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="Secret detail?"
    ).json()

    their_quote = _submit(
        client,
        email="theirs@example.com",
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "Their confidential answer"}],
    ).json()

    resp = client.get(f"/api/v1/client/quotes/{their_quote['id']}", headers=_auth(mine))
    assert resp.status_code == 404
    assert "Their confidential answer" not in resp.text

    # The owner really can read it -- otherwise the 404 above proves nothing.
    assert (
        client.get(
            f"/api/v1/client/quotes/{their_quote['id']}", headers=_auth(theirs)
        ).status_code
        == 200
    )


def test_editing_a_question_does_not_rewrite_a_submitted_answer(
    client, admin_headers, sent_emails
):
    """The stored label is what was asked at the time, not what it says today."""
    service = _make_service(client, admin_headers)
    question = _add_question(
        client, admin_headers, service["id"], question_text="How many pages?"
    ).json()
    quote = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "12"}],
    ).json()

    client.patch(
        f"/api/v1/services/{service['id']}/questions/{question['id']}",
        json={"question_text": "How many screens, roughly?"},
        headers=admin_headers,
    )

    detail = client.get(f"/api/v1/quote-requests/{quote['id']}", headers=admin_headers).json()
    assert detail["answers"][0]["question_text"] == "How many pages?"


def test_soft_deleting_a_question_leaves_submitted_answers_intact(
    client, admin_headers, sent_emails
):
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()
    quote = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "12"}],
    ).json()

    client.delete(
        f"/api/v1/services/{service['id']}/questions/{question['id']}", headers=admin_headers
    )

    detail = client.get(f"/api/v1/quote-requests/{quote['id']}", headers=admin_headers).json()
    assert detail["answers"][0]["answer"] == "12"


def test_a_multiselect_answer_is_stored_as_submitted(client, admin_headers, sent_emails):
    service = _make_service(client, admin_headers)
    question = _add_question(
        client,
        admin_headers,
        service["id"],
        question_text="Which features?",
        question_type="MULTISELECT",
        options=["Blog", "Shop", "Booking"],
    ).json()

    quote = _submit(
        client,
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "Blog, Booking"}],
    ).json()
    assert quote["answers"][0]["answer"] == "Blog, Booking"


def test_converting_a_quote_with_answers_to_a_project_still_works(
    client, admin_headers, sent_emails
):
    """The answers must not disturb the existing quote-to-project conversion."""
    owner = _make_client("convert.me@example.com")
    service = _make_service(client, admin_headers)
    question = _add_question(client, admin_headers, service["id"]).json()
    quote = _submit(
        client,
        email="convert.me@example.com",
        service_id=service["id"],
        answers=[{"question_id": question["id"], "answer": "8"}],
    ).json()

    client.patch(
        f"/api/v1/quote-requests/{quote['id']}", json={"status": "ACCEPTED"}, headers=admin_headers
    )
    resp = client.post(
        f"/api/v1/quote-requests/{quote['id']}/create-project?client_id={owner.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "A new site"
