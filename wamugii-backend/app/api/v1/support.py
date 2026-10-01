import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.crud import project as project_crud
from app.crud import support as support_crud
from app.crud import user as user_crud
from app.models.support import TicketCategory, TicketPriority, TicketStatus
from app.models.user import Role, User
from app.schemas.support import (
    SupportTicketAdminCreate,
    SupportTicketListItem,
    SupportTicketRead,
    SupportTicketUpdate,
    TicketMessageCreate,
    TicketMessageRead,
)
from app.services import notifications

router = APIRouter(prefix="/tickets", tags=["support"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]

# Transitions the client is told about. OPEN and IN_PROGRESS are internal
# workflow noise; the client only needs to hear that we're done, that it's
# closed, or that we're blocked on them.
NOTIFIABLE_STATUSES = (
    TicketStatus.RESOLVED,
    TicketStatus.CLOSED,
    TicketStatus.WAITING_ON_CLIENT,
)


def validate_project_for_ticket(db: Session, project_id: int, client_id: int) -> None:
    """
    A linked project must exist, be active, and belong to the same client —
    the rule invoices already enforce.
    """
    project = project_crud.get_by_id(db, project_id)
    if not project or not project.is_active:
        raise HTTPException(
            status_code=422, detail="project_id does not reference an active project"
        )
    if project.client_id != client_id:
        raise HTTPException(
            status_code=422, detail="project_id belongs to a different client"
        )


def validate_assignee(db: Session, assigned_to: int) -> None:
    user = user_crud.get_by_id(db, assigned_to)
    if not user or not user.is_active or user.role not in (Role.ADMIN, Role.STAFF):
        raise HTTPException(
            status_code=422,
            detail="assigned_to must reference an active ADMIN or STAFF user",
        )


def validate_client(db: Session, client_id: int) -> None:
    user = user_crud.get_by_id(db, client_id)
    if not user or not user.is_active or user.role != Role.CLIENT:
        raise HTTPException(
            status_code=422,
            detail="client_id must reference an active user with the CLIENT role",
        )


@router.post(
    "",
    response_model=SupportTicketRead,
    status_code=201,
    summary="Raise a ticket on a client's behalf (ADMIN or STAFF)",
)
def create_ticket_for_client(
    data: SupportTicketAdminCreate, db: DbDep, current_user: StaffOrAdmin
):
    validate_client(db, data.client_id)
    if data.project_id is not None:
        validate_project_for_ticket(db, data.project_id, data.client_id)

    ticket = support_crud.create_ticket(
        db,
        client_id=data.client_id,
        subject=data.subject,
        description=data.description,
        category=data.category,
        project_id=data.project_id,
        priority=data.priority,
    )
    logger.info("staff %s raised ticket %s for client %s", current_user.id, ticket.id, data.client_id)
    notifications.notify_ticket_created(db, ticket)
    return ticket


@router.get("", response_model=list[SupportTicketListItem], summary="List tickets (ADMIN or STAFF)")
def list_tickets(
    db: DbDep,
    current_user: StaffOrAdmin,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    category: TicketCategory | None = None,
    client_id: int | None = None,
    assigned_to: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    return support_crud.list_tickets(
        db,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        category=category,
        client_id=client_id,
        assigned_to=assigned_to,
        search=search,
        include_inactive=include_inactive,
    )


@router.get(
    "/{ticket_id}",
    response_model=SupportTicketRead,
    summary="Get a ticket with its full thread, internal notes included (ADMIN or STAFF)",
)
def get_ticket(ticket_id: int, db: DbDep, current_user: StaffOrAdmin):
    ticket = support_crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=SupportTicketRead,
    summary="Update a ticket's status, priority, category or assignee (ADMIN or STAFF)",
)
def update_ticket(
    ticket_id: int, data: SupportTicketUpdate, db: DbDep, current_user: StaffOrAdmin
):
    ticket = support_crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if "assigned_to" in data.model_fields_set and data.assigned_to is not None:
        validate_assignee(db, data.assigned_to)

    # Captured before the update mutates the row in place.
    old_status = ticket.status
    updated = support_crud.update_ticket(db, ticket, data)
    logger.info(
        "staff %s updated ticket %s: %s",
        current_user.id,
        ticket_id,
        data.model_dump(exclude_unset=True),
    )

    # Only a real transition into a notifiable state is an event.
    if updated.status != old_status and updated.status in NOTIFIABLE_STATUSES:
        notifications.notify_ticket_status_changed(db, updated)
    return updated


@router.post(
    "/{ticket_id}/messages",
    response_model=TicketMessageRead,
    status_code=201,
    summary="Reply on a ticket, optionally as an internal note (ADMIN or STAFF)",
)
def add_staff_message(
    ticket_id: int, data: TicketMessageCreate, db: DbDep, current_user: StaffOrAdmin
):
    ticket = support_crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    entry = support_crud.add_message(
        db,
        ticket,
        sender_id=current_user.id,
        message=data.message,
        is_internal_note=data.is_internal_note,
    )
    logger.info(
        "staff %s added %s to ticket %s",
        current_user.id,
        "an internal note" if data.is_internal_note else "a reply",
        ticket_id,
    )

    # An internal note is staff-only: it is never emailed and never notified to
    # the client. Only a real reply reaches them.
    if not data.is_internal_note:
        notifications.notify_ticket_reply_to_client(db, ticket, entry)
    return entry


@router.delete(
    "/{ticket_id}",
    response_model=SupportTicketRead,
    summary="Deactivate a ticket (ADMIN only, soft delete)",
)
def deactivate_ticket(ticket_id: int, db: DbDep, admin: AdminOnly):
    ticket = support_crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    updated = support_crud.deactivate_ticket(db, ticket)
    logger.info("admin %s deactivated ticket %s", admin.id, ticket_id)
    return updated
