from datetime import datetime, timedelta, timezone

import pytest

from app.core.config import settings
from app.crud import password_reset_token as reset_crud
from app.crud import user as user_crud
from app.models.password_reset_token import PasswordResetToken
from app.models.user import Role
from app.schemas.user import UserCreate
from app.services import email_service
from tests.conftest import TestingSessionLocal

ORIGINAL_PASSWORD = "password123"
NEW_PASSWORD = "brand-new-secret-9"


@pytest.fixture
def sent_emails(monkeypatch):
    """Capture outbound email instead of calling Brevo."""
    captured: list[dict] = []

    def _fake_send_email(to_email, to_name, subject, html_content, text_content=None):
        captured.append(
            {
                "to_email": to_email,
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }
        )
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send_email)
    return captured


def _create_user(email: str, full_name: str = "Reset User", role: Role = Role.CLIENT):
    db = TestingSessionLocal()
    try:
        return user_crud.create(
            db,
            UserCreate(full_name=full_name, email=email, password=ORIGINAL_PASSWORD),
            role=role,
        )
    finally:
        db.close()


def _tokens_for(user_id: int) -> list[PasswordResetToken]:
    db = TestingSessionLocal()
    try:
        from sqlalchemy import select

        return list(
            db.scalars(
                select(PasswordResetToken)
                .where(PasswordResetToken.user_id == user_id)
                .order_by(PasswordResetToken.id)
            ).all()
        )
    finally:
        db.close()


def _login(client, email: str, password: str):
    return client.post("/api/v1/auth/login", data={"username": email, "password": password})


def _forgot(client, email: str):
    return client.post("/api/v1/auth/forgot-password", json={"email": email})


def _reset(client, token: str, password: str = NEW_PASSWORD):
    return client.post(
        "/api/v1/auth/reset-password", json={"token": token, "password": password}
    )


# --- forgot-password --------------------------------------------------------


def test_forgot_password_creates_token_and_sends_email(client, sent_emails):
    user = _create_user("reset_real@example.com")

    resp = _forgot(client, "reset_real@example.com")
    assert resp.status_code == 200
    assert "If an account exists" in resp.json()["detail"]

    tokens = _tokens_for(user.id)
    assert len(tokens) == 1
    assert tokens[0].used_at is None
    # Cryptographically random, not a guessable value.
    assert len(tokens[0].token) >= 40
    assert str(user.id) != tokens[0].token

    assert [e["to_email"] for e in sent_emails] == ["reset_real@example.com"]
    assert sent_emails[0]["subject"] == "Reset your WAMUGII password"


def test_forgot_password_for_unknown_email_is_indistinguishable(client, sent_emails):
    """Same body, no token, no email — the endpoint can't enumerate accounts."""
    real = _create_user("reset_known@example.com")
    known = _forgot(client, "reset_known@example.com")
    sent_emails.clear()

    unknown = _forgot(client, "nobody_here_at_all@example.com")

    assert unknown.status_code == known.status_code == 200
    assert unknown.json() == known.json()
    assert sent_emails == []

    # Nothing was created for a user that doesn't exist.
    db = TestingSessionLocal()
    try:
        from sqlalchemy import func, select

        total = db.scalar(select(func.count()).select_from(PasswordResetToken))
    finally:
        db.close()
    assert total == len(_tokens_for(real.id))


def test_forgot_password_for_inactive_user_sends_nothing(client, sent_emails):
    user = _create_user("reset_inactive@example.com")
    db = TestingSessionLocal()
    try:
        user_crud.deactivate(db, db.get(type(user), user.id))
    finally:
        db.close()
    sent_emails.clear()

    resp = _forgot(client, "reset_inactive@example.com")
    assert resp.status_code == 200  # still the neutral response
    assert sent_emails == []
    assert _tokens_for(user.id) == []


def test_forgot_password_reuses_a_live_token_instead_of_spamming(client, sent_emails):
    """Repeat submissions must not mint a token or an email each time."""
    user = _create_user("reset_spam@example.com")

    _forgot(client, "reset_spam@example.com")
    assert len(_tokens_for(user.id)) == 1
    assert len(sent_emails) == 1

    for _ in range(3):
        resp = _forgot(client, "reset_spam@example.com")
        assert resp.status_code == 200

    assert len(_tokens_for(user.id)) == 1, "a duplicate token was issued"
    assert len(sent_emails) == 1, "a duplicate email was sent"


def test_forgot_password_issues_a_fresh_token_once_the_old_one_is_spent(client, sent_emails):
    user = _create_user("reset_afterspend@example.com")
    _forgot(client, "reset_afterspend@example.com")
    token = _tokens_for(user.id)[0].token

    assert _reset(client, token).status_code == 200
    sent_emails.clear()

    # The old token is used, so a new request is allowed to create another.
    assert _forgot(client, "reset_afterspend@example.com").status_code == 200
    tokens = _tokens_for(user.id)
    assert len(tokens) == 2
    assert len(sent_emails) == 1


def test_reset_url_uses_frontend_url(client, sent_emails, monkeypatch):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://wamugii.test")
    _create_user("reset_url@example.com")

    _forgot(client, "reset_url@example.com")
    html = sent_emails[0]["html"]
    assert "https://wamugii.test/reset-password?token=" in html


def test_email_omits_the_button_without_frontend_url(client, sent_emails, monkeypatch):
    monkeypatch.setattr(settings, "FRONTEND_URL", None)
    _create_user("reset_nourl@example.com")

    _forgot(client, "reset_nourl@example.com")
    html = sent_emails[0]["html"]
    assert "Reset My Password" not in html
    assert "reset-password?token=" not in html


# --- reset-password ---------------------------------------------------------


def test_reset_with_a_valid_token_changes_the_password(client, sent_emails):
    user = _create_user("reset_valid@example.com")
    _forgot(client, "reset_valid@example.com")
    token = _tokens_for(user.id)[0].token

    resp = _reset(client, token)
    assert resp.status_code == 200
    assert "reset" in resp.json()["detail"].lower()

    # Token is spent.
    assert _tokens_for(user.id)[0].used_at is not None

    # The old password is dead and the new one works.
    assert _login(client, "reset_valid@example.com", ORIGINAL_PASSWORD).status_code == 401
    new_login = _login(client, "reset_valid@example.com", NEW_PASSWORD)
    assert new_login.status_code == 200
    assert new_login.json()["access_token"]


def test_reset_with_an_expired_token_is_rejected(client, sent_emails):
    user = _create_user("reset_expired@example.com")
    _forgot(client, "reset_expired@example.com")
    token = _tokens_for(user.id)[0].token

    # Push the expiry into the past.
    db = TestingSessionLocal()
    try:
        row = db.scalar(
            __import__("sqlalchemy").select(PasswordResetToken).where(
                PasswordResetToken.token == token
            )
        )
        row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()

    resp = _reset(client, token)
    assert resp.status_code == 400
    assert resp.json()["detail"] == (
        "This reset link has expired or has already been used. Please request a new one."
    )
    # And the password was not changed.
    assert _login(client, "reset_expired@example.com", ORIGINAL_PASSWORD).status_code == 200


def test_reset_with_an_already_used_token_is_rejected(client, sent_emails):
    user = _create_user("reset_used@example.com")
    _forgot(client, "reset_used@example.com")
    token = _tokens_for(user.id)[0].token

    assert _reset(client, token).status_code == 200

    # Same string, second attempt — even though the attacker holds it.
    second = _reset(client, token, "another-password-1")
    assert second.status_code == 400
    assert "expired or has already been used" in second.json()["detail"]
    # The first reset's password still stands.
    assert _login(client, "reset_used@example.com", NEW_PASSWORD).status_code == 200


def test_reset_with_a_fabricated_token_is_rejected(client):
    resp = _reset(client, "totally-made-up-token-value")
    assert resp.status_code == 400
    assert "expired or has already been used" in resp.json()["detail"]


def test_expired_used_and_fake_tokens_all_return_the_same_message(client, sent_emails):
    """An attacker must not be able to tell the three failures apart."""
    user = _create_user("reset_same@example.com")
    _forgot(client, "reset_same@example.com")
    used_token = _tokens_for(user.id)[0].token
    _reset(client, used_token)

    other = _create_user("reset_same2@example.com")
    _forgot(client, "reset_same2@example.com")
    expired_token = _tokens_for(other.id)[0].token
    db = TestingSessionLocal()
    try:
        import sqlalchemy

        row = db.scalar(
            sqlalchemy.select(PasswordResetToken).where(
                PasswordResetToken.token == expired_token
            )
        )
        row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    finally:
        db.close()

    responses = [
        _reset(client, used_token),
        _reset(client, expired_token),
        _reset(client, "fake-token"),
    ]
    assert {r.status_code for r in responses} == {400}
    assert len({r.json()["detail"] for r in responses}) == 1


def test_reset_invalidates_all_outstanding_tokens_for_that_user(client, sent_emails):
    """
    A second link issued earlier must die too — prevents replay if more than
    one was somehow in flight.
    """
    user = _create_user("reset_multi@example.com")

    # Two tokens created directly, bypassing the reuse guard on the endpoint.
    db = TestingSessionLocal()
    try:
        first = reset_crud.create_for_user(db, user.id)
        second = reset_crud.create_for_user(db, user.id)
        first_token, second_token = first.token, second.token
    finally:
        db.close()
    assert len(_tokens_for(user.id)) == 2

    assert _reset(client, first_token).status_code == 200

    # Both are spent now.
    assert all(t.used_at is not None for t in _tokens_for(user.id))
    replay = _reset(client, second_token, "yet-another-pass-1")
    assert replay.status_code == 400
    # The password from the successful reset still stands.
    assert _login(client, "reset_multi@example.com", NEW_PASSWORD).status_code == 200


def test_reset_for_a_deactivated_user_is_rejected(client, sent_emails):
    user = _create_user("reset_deactivated@example.com")
    _forgot(client, "reset_deactivated@example.com")
    token = _tokens_for(user.id)[0].token

    db = TestingSessionLocal()
    try:
        from app.models.user import User

        user_crud.deactivate(db, db.get(User, user.id))
    finally:
        db.close()

    resp = _reset(client, token)
    assert resp.status_code == 400
    assert "expired or has already been used" in resp.json()["detail"]


def test_short_passwords_are_rejected(client, sent_emails):
    user = _create_user("reset_short@example.com")
    _forgot(client, "reset_short@example.com")
    token = _tokens_for(user.id)[0].token

    resp = _reset(client, token, "short")
    assert resp.status_code == 422
    # The token survives a rejected attempt so the user can retry.
    assert _tokens_for(user.id)[0].used_at is None


def test_reset_password_requires_no_authentication(client, sent_emails):
    """Both endpoints must work for a logged-out user."""
    _create_user("reset_anon@example.com")
    assert _forgot(client, "reset_anon@example.com").status_code == 200
    assert _reset(client, "nope").status_code == 400  # 400, never 401


# --- token helper behaviour -------------------------------------------------


def test_generated_tokens_are_unique_and_urlsafe():
    tokens = {reset_crud.generate_token() for _ in range(200)}
    assert len(tokens) == 200
    for token in tokens:
        assert token.replace("-", "").replace("_", "").isalnum()


def test_token_ttl_is_one_hour(client, sent_emails):
    user = _create_user("reset_ttl@example.com")
    _forgot(client, "reset_ttl@example.com")
    row = _tokens_for(user.id)[0]

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    delta = expires - datetime.now(timezone.utc)
    assert timedelta(minutes=58) < delta <= timedelta(hours=1)
