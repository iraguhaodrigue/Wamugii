"""Health check, for uptime monitors and the container's HEALTHCHECK."""

import logging

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.api.deps import DbDep
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness and database check (public, no login)",
)
def health(db: DbDep, response: Response) -> dict:
    """
    200 while the API can reach the database, 503 when it cannot.

    The body is deliberately tiny and says nothing an attacker could use: no
    driver name, no host, no error text. The real reason is logged instead,
    where an operator can read it. The database probe is a plain `SELECT 1`,
    which is cheap enough for a monitor to call every minute.
    """
    database = "ok"
    try:
        db.execute(text("SELECT 1")).scalar()
    except Exception:
        logger.exception("health check: database probe failed")
        database = "error"
        response.status_code = 503

    return {
        "status": "ok" if database == "ok" else "error",
        "database": database,
        "version": settings.APP_VERSION,
    }
