from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.support import (
    OPEN_STATUSES,
    SupportTicket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)
from app.schemas.support import SupportTicketUpdate


def get_ticket(db: Session, ticket_id: int) -> SupportTicket | None:
    return db.get(SupportTicket, ticket_id)


def get_ticket_for_client(db: Session, ticket_id: int, client_id: int) -> SupportTicket | None:
    """None for anything that isn't this client's, which the router turns into 404."""
    return db.scalar(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id,
            SupportTicket.client_id == client_id,
            SupportTicket.is_active.is_(True),
        )
    )


def list_tickets(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    category: TicketCategory | None = None,
    client_id: int | None = None,
    assigned_to: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[SupportTicket]:
    query = select(SupportTicket)
    if not include_inactive:
        query = query.where(SupportTicket.is_active.is_(True))
    if status is not None:
        query = query.where(SupportTicket.status == status)
    if priority is not None:
        query = query.where(SupportTicket.priority == priority)
    if category is not None:
        query = query.where(SupportTicket.category == category)
    if client_id is not None:
        query = query.where(SupportTicket.client_id == client_id)
    if assigned_to is not None:
        query = query.where(SupportTicket.assigned_to == assigned_to)
    if search:
        query = query.where(func.lower(SupportTicket.subject).contains(search.lower()))
    # Most-recently-touched first: a ticket with a new reply is what staff want.
    query = query.order_by(SupportTicket.updated_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def list_tickets_for_client(
    db: Session,
    client_id: int,
    *,
    limit: int = 20,
    offset: int = 0,
    status: TicketStatus | None = None,
) -> list[SupportTicket]:
    query = select(SupportTicket).where(
        SupportTicket.client_id == client_id,
        SupportTicket.is_active.is_(True),
    )
    if status is not None:
        query = query.where(SupportTicket.status == status)
    query = query.order_by(SupportTicket.updated_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def create_ticket(
    db: Session,
    *,
    client_id: int,
    subject: str,
    description: str,
    category: TicketCategory,
    project_id: int | None = None,
    priority: TicketPriority = TicketPriority.MEDIUM,
) -> SupportTicket:
    ticket = SupportTicket(
        client_id=client_id,
        project_id=project_id,
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        status=TicketStatus.OPEN,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(db: Session, ticket: SupportTicket, data: SupportTicketUpdate) -> SupportTicket:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def deactivate_ticket(db: Session, ticket: SupportTicket) -> SupportTicket:
    ticket.is_active = False
    db.commit()
    db.refresh(ticket)
    return ticket


def add_message(
    db: Session,
    ticket: SupportTicket,
    *,
    sender_id: int,
    message: str,
    is_internal_note: bool = False,
) -> TicketMessage:
    """
    Append to the thread and touch the ticket so it sorts to the top of the
    staff list. `updated_at` has onupdate=now() but only fires when a column
    actually changes, so the status write below is what bumps it — see
    `reopen_if_waiting`, which the router calls for client replies.
    """
    entry = TicketMessage(
        ticket_id=ticket.id,
        sender_id=sender_id,
        message=message,
        is_internal_note=is_internal_note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def reopen_if_waiting(db: Session, ticket: SupportTicket) -> bool:
    """
    A client reply on a WAITING_ON_CLIENT ticket puts the ball back with us.
    Returns True when the status actually moved.
    """
    if ticket.status != TicketStatus.WAITING_ON_CLIENT:
        return False
    ticket.status = TicketStatus.OPEN
    db.commit()
    db.refresh(ticket)
    return True


def visible_messages(ticket: SupportTicket) -> list[TicketMessage]:
    """The thread minus staff-only notes — what a client is allowed to read."""
    return [m for m in ticket.messages if not m.is_internal_note]


def count_open_tickets(db: Session) -> int:
    """SQL COUNT for the admin dashboard's support block."""
    return (
        db.scalar(
            select(func.count())
            .select_from(SupportTicket)
            .where(
                SupportTicket.status.in_(OPEN_STATUSES),
                SupportTicket.is_active.is_(True),
            )
        )
        or 0
    )
