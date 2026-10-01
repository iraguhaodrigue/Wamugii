from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.support import TicketCategory, TicketPriority, TicketStatus


class TicketMessageCreate(BaseModel):
    """
    A reply. `is_internal_note` is accepted here but only honoured for
    ADMIN/STAFF — the client endpoint ignores it entirely (see
    api/v1/support.add_client_message), so a client cannot post a note that
    hides itself from their own view or skips the staff email.
    """

    message: str = Field(min_length=1)
    is_internal_note: bool = False


class TicketMessageRead(BaseModel):
    """Staff view of a thread entry, including the internal-note flag."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    sender_id: int
    message: str
    is_internal_note: bool
    created_at: datetime


class SupportTicketCreate(BaseModel):
    """What a client submits. Priority/status/assignee are staff decisions."""

    subject: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    category: TicketCategory = TicketCategory.GENERAL
    project_id: int | None = None


class SupportTicketAdminCreate(SupportTicketCreate):
    """Staff may also raise a ticket on a client's behalf."""

    client_id: int
    priority: TicketPriority = TicketPriority.MEDIUM


class SupportTicketUpdate(BaseModel):
    """Staff-only changes."""

    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    category: TicketCategory | None = None
    assigned_to: int | None = None


class SupportTicketRead(BaseModel):
    """Full staff view, with the whole thread including internal notes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    project_id: int | None
    subject: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    assigned_to: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: list[TicketMessageRead] = []


class SupportTicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    project_id: int | None
    subject: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    assigned_to: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# --- client-facing ----------------------------------------------------------


class ClientTicketMessageRead(BaseModel):
    """
    A thread entry as its client sees it.

    `is_internal_note` is not declared here at all, and the router filters those
    messages out before serializing — so an internal note can neither appear nor
    be inferred from a missing id, since ids aren't sequential per view.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: int
    message: str
    created_at: datetime


class ClientTicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int | None
    subject: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime


class ClientTicketDetail(BaseModel):
    """
    The client's own ticket. Carries no `assigned_to` (who internally owns it
    isn't the client's business) and no internal notes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int | None
    subject: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    messages: list[ClientTicketMessageRead] = []
