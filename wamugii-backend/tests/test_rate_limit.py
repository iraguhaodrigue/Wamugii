"""
Rate limits on the endpoints abuse actually targets.

The suite disables rate limiting globally (see conftest) so the other 500-odd
tests can register and sign in freely. These tests turn it back on for
themselves. The limiters read their ceiling from settings at import time, so
the numbers here follow the defaults in config.py rather than being patched.

No test asserts on timing: the windows are minutes to hours, so each test only
has to push one key past its ceiling.
"""

from fastapi import HTTPException

from app.core.config import settings
from app.services import domain_search


def _ip(address: str) -> dict:
    """Headers that make the request look like it came from `address` via nginx."""
    return {"X-Forwarded-For": address}


# --------------------------------------------------------------------------
# login
# --------------------------------------------------------------------------

def test_login_is_limited_per_ip(client, limits_on):
    limit = settings.RATE_LIMIT_LOGIN_PER_MINUTE
    body = {"username": "nobody@example.com", "password": "wrong-password"}

    # Wrong credentials, so each of these is a 401 -- the point is that they
    # are allowed through to be judged at all.
    for _ in range(limit):
        r = client.post("/api/v1/auth/login", data=body, headers=_ip("5.5.5.5"))
        assert r.status_code == 401

    blocked = client.post("/api/v1/auth/login", data=body, headers=_ip("5.5.5.5"))
    assert blocked.status_code == 429
    assert "too many attempts" in blocked.json()["detail"].lower()


def test_login_limit_does_not_block_a_different_ip(client, limits_on):
    body = {"username": "nobody@example.com", "password": "wrong-password"}
    for _ in range(settings.RATE_LIMIT_LOGIN_PER_MINUTE + 1):
        client.post("/api/v1/auth/login", data=body, headers=_ip("5.5.5.5"))

    # A different visitor is unaffected.
    other = client.post("/api/v1/auth/login", data=body, headers=_ip("6.6.6.6"))
    assert other.status_code == 401


def test_login_limit_keys_on_the_last_forwarded_entry(client, limits_on):
    """
    Only the entry nginx appends is trusted. A visitor can type anything into
    X-Forwarded-For, so keying on the first entry would let them pick a fresh
    bucket per request and bypass the limit.
    """
    body = {"username": "nobody@example.com", "password": "wrong-password"}
    for _ in range(settings.RATE_LIMIT_LOGIN_PER_MINUTE):
        client.post("/api/v1/auth/login", data=body, headers=_ip("1.1.1.1, 7.7.7.7"))

    # Different spoofed prefix, same real address -> still blocked.
    assert client.post(
        "/api/v1/auth/login", data=body, headers=_ip("9.9.9.9, 7.7.7.7")
    ).status_code == 429

    # Same spoofed prefix, different real address -> allowed.
    assert client.post(
        "/api/v1/auth/login", data=body, headers=_ip("9.9.9.9, 8.8.8.8")
    ).status_code == 401


def test_login_failures_are_limited_per_email_across_ips(client, limits_on):
    """
    The per-email limit is what stops a botnet spreading one account's guesses
    over many addresses. Each attempt comes from its own IP so the per-IP limit
    is never the thing that trips.
    """
    email = "target@example.com"
    ceiling = settings.RATE_LIMIT_LOGIN_FAILURES_PER_EMAIL
    body = {"username": email, "password": "wrong-password"}

    for i in range(ceiling):
        r = client.post("/api/v1/auth/login", data=body, headers=_ip(f"10.0.0.{i}"))
        assert r.status_code == 401

    blocked = client.post("/api/v1/auth/login", data=body, headers=_ip("10.0.1.1"))
    assert blocked.status_code == 429

    # A different account is still reachable from a fresh address.
    assert client.post(
        "/api/v1/auth/login",
        data={"username": "someone-else@example.com", "password": "wrong-password"},
        headers=_ip("10.0.1.2"),
    ).status_code == 401


def test_successful_logins_do_not_count_towards_the_email_limit(client, limits_on, client_headers):
    """
    Only failures are recorded, so someone who keeps signing in correctly is
    never locked out of their own account. The per-IP limit still applies, so
    this stays under it.
    """
    body = {"username": "client@example.com", "password": "password123"}
    for i in range(settings.RATE_LIMIT_LOGIN_PER_MINUTE):
        r = client.post("/api/v1/auth/login", data=body, headers=_ip(f"11.0.0.{i}"))
        assert r.status_code == 200

    # Far past the per-email ceiling in count, but none of them were failures.


# --------------------------------------------------------------------------
# registration
# --------------------------------------------------------------------------

def test_register_is_limited_per_ip(client, limits_on):
    limit = settings.RATE_LIMIT_REGISTER_PER_HOUR
    for i in range(limit):
        r = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": f"Person {i}",
                "email": f"signup{i}@example.com",
                "password": "password123",
            },
            headers=_ip("12.0.0.1"),
        )
        assert r.status_code == 201

    blocked = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "One Too Many",
            "email": "toomany@example.com",
            "password": "password123",
        },
        headers=_ip("12.0.0.1"),
    )
    assert blocked.status_code == 429


def test_register_team_member_has_its_own_limit(client, limits_on):
    """
    The two sign-up forms do not share a counter: using up one must not close
    the other.
    """
    for i in range(settings.RATE_LIMIT_REGISTER_PER_HOUR):
        client.post(
            "/api/v1/auth/register",
            json={
                "full_name": f"Person {i}",
                "email": f"shared{i}@example.com",
                "password": "password123",
            },
            headers=_ip("12.0.0.2"),
        )

    # Client sign-up is spent for this IP...
    assert client.post(
        "/api/v1/auth/register",
        json={"full_name": "X", "email": "x@example.com", "password": "password123"},
        headers=_ip("12.0.0.2"),
    ).status_code == 429

    # ...but the team-member form still answers.
    assert client.post(
        "/api/v1/auth/register-team-member",
        json={
            "full_name": "Team Person",
            "email": "teamperson@example.com",
            "password": "password123",
        },
        headers=_ip("12.0.0.2"),
    ).status_code != 429


# --------------------------------------------------------------------------
# password reset
# --------------------------------------------------------------------------

def test_forgot_password_is_limited_per_ip(client, limits_on):
    for i in range(settings.RATE_LIMIT_FORGOT_PASSWORD_PER_WINDOW):
        r = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": f"whoever{i}@example.com"},
            headers=_ip("13.0.0.1"),
        )
        assert r.status_code == 200

    blocked = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "another@example.com"},
        headers=_ip("13.0.0.1"),
    )
    assert blocked.status_code == 429


def test_forgot_password_is_also_limited_per_email(client, limits_on):
    """
    Keyed on the address too, so the same mailbox cannot be mail-bombed from a
    different IP each time.
    """
    email = "victim@example.com"
    for i in range(settings.RATE_LIMIT_FORGOT_PASSWORD_PER_WINDOW):
        r = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": email},
            headers=_ip(f"14.0.0.{i}"),
        )
        assert r.status_code == 200

    blocked = client.post(
        "/api/v1/auth/forgot-password", json={"email": email}, headers=_ip("14.9.9.9")
    )
    assert blocked.status_code == 429


def test_forgot_password_429_reveals_nothing_about_the_account(client, limits_on, client_headers):
    """
    A real address and an unknown one must be indistinguishable, at 200 and at
    429 alike -- otherwise the limit becomes the enumeration oracle the neutral
    200 body was written to avoid.
    """
    real, fake = "client@example.com", "no-such-person@example.com"

    first = client.post("/api/v1/auth/forgot-password", json={"email": real}, headers=_ip("15.0.0.1"))
    second = client.post("/api/v1/auth/forgot-password", json={"email": fake}, headers=_ip("15.0.0.2"))
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()

    # Push both addresses past the per-email ceiling from fresh IPs.
    for email, net in ((real, 16), (fake, 17)):
        for i in range(settings.RATE_LIMIT_FORGOT_PASSWORD_PER_WINDOW):
            client.post(
                "/api/v1/auth/forgot-password",
                json={"email": email},
                headers=_ip(f"{net}.0.0.{i}"),
            )

    blocked_real = client.post(
        "/api/v1/auth/forgot-password", json={"email": real}, headers=_ip("16.9.9.9")
    )
    blocked_fake = client.post(
        "/api/v1/auth/forgot-password", json={"email": fake}, headers=_ip("17.9.9.9")
    )
    assert blocked_real.status_code == blocked_fake.status_code == 429
    assert blocked_real.json() == blocked_fake.json()


def test_reset_password_is_limited_per_ip(client, limits_on):
    """
    The body has to be well formed for this to mean anything: FastAPI validates
    it before the handler runs, so a malformed body never reaches the limiter
    (it also never reaches the database, so nothing is spent on it).
    """
    body = {"token": "not-a-real-token", "password": "password123"}
    for _ in range(settings.RATE_LIMIT_RESET_PASSWORD_PER_WINDOW):
        r = client.post("/api/v1/auth/reset-password", json=body, headers=_ip("18.0.0.1"))
        assert r.status_code == 400

    blocked = client.post("/api/v1/auth/reset-password", json=body, headers=_ip("18.0.0.1"))
    assert blocked.status_code == 429


def test_refresh_is_limited_per_ip(client, limits_on):
    for _ in range(settings.RATE_LIMIT_REFRESH_PER_MINUTE):
        r = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "nonsense"},
            headers=_ip("19.0.0.1"),
        )
        assert r.status_code == 401

    blocked = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "nonsense"}, headers=_ip("19.0.0.1")
    )
    assert blocked.status_code == 429


# --------------------------------------------------------------------------
# public forms
# --------------------------------------------------------------------------

def test_quote_request_is_limited_per_ip(client, limits_on):
    payload = {
        "full_name": "Form Filler",
        "email": "forms@example.com",
        "phone": "0788000000",
        "project_title": "A website",
        "project_description": "Please build me a website for my shop.",
    }
    for _ in range(settings.RATE_LIMIT_QUOTE_PER_HOUR):
        r = client.post("/api/v1/quote-requests", json=payload, headers=_ip("20.0.0.1"))
        assert r.status_code == 201

    blocked = client.post("/api/v1/quote-requests", json=payload, headers=_ip("20.0.0.1"))
    assert blocked.status_code == 429

    # Another visitor can still submit.
    assert client.post(
        "/api/v1/quote-requests", json=payload, headers=_ip("20.0.0.2")
    ).status_code == 201


def test_domain_order_is_limited_per_user(client, limits_on, client_headers, monkeypatch):
    """
    Keyed on the account, not the address, so moving between networks does not
    reset it.

    The ordering service is stubbed out: the limiter runs before it, and the
    real path makes live registry lookups, which the suite never does.
    """
    def _refuse(*_args, **_kwargs):
        raise HTTPException(status_code=422, detail="stubbed out for this test")

    monkeypatch.setattr(domain_search, "order", _refuse)

    payload = {"domain_name": "kigalishop.rw", "years": 1}
    for _ in range(settings.RATE_LIMIT_DOMAIN_ORDER_PER_HOUR):
        r = client.post(
            "/api/v1/client/domains/order",
            json=payload,
            headers={**client_headers, **_ip("21.0.0.1")},
        )
        assert r.status_code == 422

    # Same account, different network -> still blocked.
    blocked = client.post(
        "/api/v1/client/domains/order",
        json=payload,
        headers={**client_headers, **_ip("21.9.9.9")},
    )
    assert blocked.status_code == 429
