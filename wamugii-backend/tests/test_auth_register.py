"""
Registration password rules.

`POST /auth/register` previously accepted any password, including a single
character — the 8-character minimum existed only in the frontend's zod schema.
These tests pin the server-side rule so it can't regress.
"""

import pytest

from app.schemas.user import MIN_PASSWORD_LENGTH


def _register(client, email: str, password: str):
    return client.post(
        "/api/v1/auth/register",
        json={"full_name": "Register Test", "email": email, "password": password},
    )


def test_registration_rejects_a_seven_character_password(client):
    resp = _register(client, "reg_seven@example.com", "seven77")
    assert len(resp.request.read()) > 0  # sanity: the body was actually sent
    assert resp.status_code == 422


@pytest.mark.parametrize("password", ["a", "short", "1234567"])
def test_registration_rejects_passwords_below_the_minimum(client, password):
    """A 1-character password was the specific gap this closes."""
    assert len(password) < MIN_PASSWORD_LENGTH
    resp = _register(client, f"reg_{len(password)}@example.com", password)
    assert resp.status_code == 422


def test_registration_accepts_exactly_the_minimum(client):
    """The boundary is inclusive — 8 characters is allowed."""
    password = "a" * MIN_PASSWORD_LENGTH
    resp = _register(client, "reg_boundary@example.com", password)
    assert resp.status_code == 201

    # ...and the account it created actually works.
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "reg_boundary@example.com", "password": password},
    )
    assert login.status_code == 200


def test_registration_still_works_normally(client):
    """The new rule must not disturb an ordinary sign-up."""
    resp = _register(client, "reg_normal@example.com", "password123")
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "reg_normal@example.com"
    assert body["role"] == "CLIENT"
    # The hash is never echoed back.
    assert "password" not in body
    assert "password_hash" not in body


def test_duplicate_email_still_returns_400_not_422(client):
    """Length validation must not mask the existing duplicate-email error."""
    _register(client, "reg_dupe@example.com", "password123")
    again = _register(client, "reg_dupe@example.com", "password123")
    assert again.status_code == 400
    assert again.json()["detail"] == "Email already registered"


def test_registration_and_reset_share_one_minimum(client):
    """
    Both endpoints enforce the same number, so a password that's too short to
    register with is also too short to reset to.
    """
    short = "a" * (MIN_PASSWORD_LENGTH - 1)
    assert _register(client, "reg_shared@example.com", short).status_code == 422

    reset = client.post(
        "/api/v1/auth/reset-password", json={"token": "irrelevant", "password": short}
    )
    # 422 from validation, not 400 — the password is rejected before the token
    # is even considered.
    assert reset.status_code == 422
