import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import (
    TOKEN_TTL_HOURS,
    PasswordResetToken,
)


def generate_token() -> str:
    """Cryptographically random, URL-safe, ~43 chars. Never guessable."""
    return secrets.token_urlsafe(32)


def _as_utc(value: datetime) -> datetime:
    """
    SQLite drops tzinfo even on a DateTime(timezone=True) column, so a value
    read back can be naive while `datetime.now(timezone.utc)` is aware, and
    comparing the two raises. Treat a naive value as UTC — which is what was
    written.
    """
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def is_usable(row: PasswordResetToken, *, now: datetime | None = None) -> bool:
    """Unused and not yet expired."""
    if row.used_at is not None:
        return False
    moment = now or datetime.now(timezone.utc)
    return _as_utc(row.expires_at) > moment


def create_for_user(db: Session, user_id: int) -> PasswordResetToken:
    row = PasswordResetToken(
        user_id=user_id,
        token=generate_token(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_by_token(db: Session, token: str) -> PasswordResetToken | None:
    """
    Raw lookup with no validity filtering — the caller checks usability, so an
    expired token and an already-used one can be answered with the same message
    rather than one 404ing and the other 400ing.
    """
    return db.scalar(select(PasswordResetToken).where(PasswordResetToken.token == token))


def get_usable_for_user(db: Session, user_id: int) -> PasswordResetToken | None:
    """
    An existing unused, unexpired token for this user, if any.

    Used to avoid minting a fresh token (and a fresh email) every time someone
    hammers the forgot-password form.
    """
    rows = db.scalars(
        select(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
        .order_by(PasswordResetToken.created_at.desc())
    ).all()
    # Expiry is compared in Python so the naive/aware mismatch above is handled
    # in exactly one place.
    for row in rows:
        if is_usable(row):
            return row
    return None


def mark_used(db: Session, row: PasswordResetToken) -> PasswordResetToken:
    row.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def invalidate_all_for_user(db: Session, user_id: int, *, commit: bool = True) -> int:
    """
    Spend every unused token this user holds.

    Called after a successful reset so that any other link that was issued —
    a second request, a forwarded email — is dead too, not just the one that
    was clicked. Returns how many were invalidated.
    """
    rows = db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
    ).all()
    now = datetime.now(timezone.utc)
    for row in rows:
        row.used_at = now
    if commit:
        db.commit()
    return len(rows)
