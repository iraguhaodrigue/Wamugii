import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificationType(str, enum.Enum):
    QUOTE_SUBMITTED = "QUOTE_SUBMITTED"
    QUOTE_STATUS_CHANGED = "QUOTE_STATUS_CHANGED"
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_STATUS_CHANGED = "PROJECT_STATUS_CHANGED"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    FILE_UPLOADED = "FILE_UPLOADED"
    INVOICE_CREATED = "INVOICE_CREATED"
    # Nothing emits INVOICE_DUE yet: it needs a scheduled sweep over due dates
    # and this project has no scheduler/worker. Kept in the enum so the value is
    # stable when that job is added — see services/notifications.py.
    INVOICE_DUE = "INVOICE_DUE"
    PAYMENT_RECORDED = "PAYMENT_RECORDED"


class Notification(Base):
    """
    An in-app message for exactly one recipient. Created by the system when
    events happen (see services/notifications.py) — never by a client, which is
    why there is no create endpoint.

    `related_type` / `related_id` are a loose pointer to the resource the
    notification is about (e.g. "invoice", 42) so the frontend can deep-link.
    Deliberately not a real FK: one column has to point at several different
    tables, and a dangling pointer must never block reading the notification.

    No `is_active` column: unlike the other modules there is no delete endpoint
    here, so a soft-delete flag would never be written. Read state is tracked by
    `is_read` instead.
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    related_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    related_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
