"""The health endpoint and the security headers every response carries."""

from sqlalchemy.exc import OperationalError

from app.core.config import settings


def test_health_is_public_and_reports_the_database(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {
        "status": "ok",
        "database": "ok",
        "version": settings.APP_VERSION,
    }


def test_health_returns_503_when_the_database_is_down(client, monkeypatch):
    """
    A monitor has to be able to tell "the process is up" from "the process is
    up but cannot reach its database", so this is a 503 rather than a 200.
    """
    from app.core import database

    class _BrokenSession:
        def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

        def close(self):
            pass

    def _broken_db():
        yield _BrokenSession()

    monkeypatch.setitem(client.app.dependency_overrides, database.get_db, _broken_db)

    r = client.get("/api/v1/health")
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "error"
    assert body["database"] == "error"


def test_health_body_leaks_no_internal_detail(client, monkeypatch):
    """The failure reason is logged, never returned."""
    from app.core import database

    secret_ish = "postgresql://wamugii:sup3rs3cret@db:5432/wamugii"

    class _BrokenSession:
        def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception(secret_ish))

        def close(self):
            pass

    monkeypatch.setitem(
        client.app.dependency_overrides, database.get_db, lambda: iter([_BrokenSession()])
    )

    r = client.get("/api/v1/health")
    assert r.status_code == 503
    assert secret_ish not in r.text
    assert "sup3rs3cret" not in r.text
    # Only the three agreed keys come back.
    assert set(r.json()) == {"status", "database", "version"}


def test_security_headers_are_set_on_api_responses(client):
    r = client.get("/api/v1/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert r.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


def test_security_headers_are_set_on_errors_too(client):
    """
    A 404 and a 401 are responses like any other -- a header that only appears
    on the happy path protects nothing.
    """
    for path in ("/api/v1/no-such-endpoint", "/api/v1/users/me"):
        r = client.get(path)
        assert r.status_code >= 400
        assert r.headers["X-Content-Type-Options"] == "nosniff"
        assert r.headers["X-Frame-Options"] == "DENY"
