import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TicketCategory(str, enum.Enum):
    GENERAL = "GENERAL"
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    PROJECT_CHANGE = "PROJECT_CHANGE"
    HOSTING = "HOSTING"
    OTHER = "OTHER"


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_ON_CLIENT = "WAITING_ON_CLIENT"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


# Statuses that mean the ticket still needs attention — used by the dashboard
# count and by the "open" reading of a ticket generally.
OPEN_STATUSES = (
    TicketStatus.OPEN,
    TicketStatus.IN_PROGRESS,
    TicketStatus.WAITING_ON_CLIENT,
)


class SupportTicket(Base):
    """
    A support request raised by a logged-in client.

    Public visitors don't reach this — they use the existing quote form — so
    `client_id` is always a real account rather than a loose email like
    QuoteRequest carries.

    `project_id` is optional; when set it must belong to the same client, the
    same rule invoices enforce.
    """

    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True, index=True
    )

    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    category: Mapped[TicketCategory] = mapped_column(
        Enum(TicketCategory), default=TicketCategory.GENERAL, index=True
    )
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority), default=TicketPriority.MEDIUM, index=True
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), default=TicketStatus.OPEN, index=True
    )

    # A STAFF/ADMIN owner. Null means "nobody has picked it up yet", which is
    # why replies fan out to the whole team in that case.
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client = relationship("User", foreign_keys=[client_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    project = relationship("Project")
    messages = relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.id",
    )


class TicketMessage(Base):
    """
    One entry in a ticket's thread.

    `is_internal_note` marks a staff-only note: it is filtered out of every
    client-facing response and never emailed. Only staff can set it — see
    api/v1/support.

    No soft-delete flag: a thread is an audit trail of what was said, so
    messages are not removed.
    """

    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    message: Mapped[str] = mapped_column(Text)
    is_internal_note: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("SupportTicket", back_populates="messages")
    sender = relationship("User")
