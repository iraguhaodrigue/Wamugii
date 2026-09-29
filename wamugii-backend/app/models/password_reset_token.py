from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# secrets.token_urlsafe(32) yields 43 URL-safe characters; the column is sized
# generously so the length can be raised later without a migration.
TOKEN_MAX_LENGTH = 128

# How long a reset link stays usable.
TOKEN_TTL_HOURS = 1


class PasswordResetToken(Base):
    """
    A single-use, time-limited password reset token.

    No `is_active` soft-delete flag: a token's lifecycle is fully described by
    `expires_at` (it ages out) and `used_at` (it is spent). Rows are kept after
    use so a replayed link can be recognised as already-used rather than simply
    unknown.

    The token string itself is cryptographically random (secrets.token_urlsafe)
    — never an id, a hash of the email, or anything else guessable — and is
    unique-indexed so a lookup is a single indexed hit.
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    token: Mapped[str] = mapped_column(String(TOKEN_MAX_LENGTH), unique=True, index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
