from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DomainSearch(Base):
    """
    One row per domain search, for the admin dashboard's "what are people
    looking for" panel. Only the searched name and counts are kept -- never an
    IP address -- and `user_id` is set only when a signed-in user searched.
    """

    __tablename__ = "domain_searches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    query: Mapped[str] = mapped_column(String(100), index=True)
    available_count: Mapped[int] = mapped_column(Integer, default=0)
    taken_count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
