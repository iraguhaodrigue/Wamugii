import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, DbDep, require_roles
from app.api.v1.support import validate_project_for_ticket
from app.crud import client as client_crud
from app.crud import company_settings as settings_crud
from app.crud import domain as domain_crud
from app.crud import hosting as hosting_crud
from app.crud import project as project_crud
from app.crud import project_milestone as milestone_crud
from app.crud import service as service_crud
from app.crud import support as support_crud
from app.models.domain import DomainStatus
from app.models.invoice import InvoiceStatus
from app.models.project import ProjectStatus
from app.models.quote_request import QuoteStatus
from app.models.support import SupportTicket, TicketStatus
from app.models.user import Role, User
from app.schemas.client import (
    ClientActivityItem,
    ClientDashboardRead,
    ClientDashboardSummary,
    ClientHostingDetail,
    ClientHostingListItem,
    ClientInvoiceDetail,
    ClientInvoiceListItem,
    ClientMilestoneListItem,
    ClientProjectDetail,
    ClientProjectListItem,
    ClientQuoteDetail,
    ClientQuoteListItem,
    ClientUserRead,
)
from app.schemas.domain import ClientDomainDetail, ClientDomainListItem
from app.schemas.support import (
    ClientTicketDetail,
    ClientTicketListItem,
    ClientTicketMessageRead,
    SupportTicketCreate,
    TicketMessageCreate,
)
from app.services import notifications

router = APIRouter(prefix="/client", tags=["client"])
logger = logging.getLogger(__name__)

ClientOnly = Annotated[User, Depends(require_roles(Role.CLIENT))]


def _client_ticket_detail(ticket: SupportTicket) -> ClientTicketDetail:
    """
    Build the client's view of a ticket with internal notes stripped.

    Done explicitly rather than by relying on the schema alone: the thread is a
    list, so a staff-only note would otherwise still occupy an entry.
    """
    detail = ClientTicketDetail.model_validate(ticket)
    detail.messages = [
        ClientTicketMessageRead.model_validate(m) for m in support_crud.visible_messages(ticket)
    ]
    return detail


@router.get("/dashboard", response_model=ClientDashboardRead, summary="Get client dashboard")
def get_dashboard(db: DbDep, current_user: ClientOnly):
    """Get the client dashboard with summary, recent projects, quotes, and activity."""
    # Get summary statistics
    summary_data = client_crud.get_dashboard_summary(db, current_user.id, current_user.email)

    # Get recent projects with progress
    recent_projects_list = []
    for project in client_crud.get_recent_projects(db, current_user.id, limit=5):
        progress = milestone_crud.get_project_progress(db, project.id)
        recent_projects_list.append(
            ClientProjectListItem(
                id=project.id,
                title=project.title,
                status=project.status,
                priority=project.priority,
                deadline=project.deadline,
                progress_percentage=progress["progress_percentage"],
                created_at=project.created_at,
            )
        )

    # Get recent quotes
    recent_quotes_list = [
        ClientQuoteListItem.model_validate(quote)
        for quote in client_crud.get_recent_quotes(db, current_user.email, limit=5)
    ]

    # Get recent activity
    activity_data = client_crud.generate_recent_activity(
        db, current_user.id, current_user.email, limit=10
    )
    recent_activity = [ClientActivityItem(**item) for item in activity_data]

    return ClientDashboardRead(
        user=ClientUserRead(
            id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
        ),
        summary=ClientDashboardSummary(**summary_data),
        recent_projects=recent_projects_list,
        recent_quotes=recent_quotes_list,
        recent_activity=recent_activity,
    )


@router.get("/projects", response_model=list[ClientProjectListItem], summary="List client projects")
def list_projects(
    db: DbDep,
    current_user: ClientOnly,
    status: ProjectStatus | None = None,
    search: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all projects belonging to the client."""
    projects = client_crud.get_client_projects(
        db, current_user.id, limit=limit, offset=offset, status=status, search=search
    )

    result = []
    for project in projects:
        progress = milestone_crud.get_project_progress(db, project.id)
        result.append(
            ClientProjectListItem(
                id=project.id,
                title=project.title,
                status=project.status,
                priority=project.priority,
                deadline=project.deadline,
                progress_percentage=progress["progress_percentage"],
                created_at=project.created_at,
            )
        )

    return result


@router.get(
    "/projects/{project_id}",
    response_model=ClientProjectDetail,
    summary="Get a client project",
)
def get_project(project_id: int, db: DbDep, current_user: ClientOnly):
    """Get detailed information about a project."""
    project = client_crud.get_client_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    progress = milestone_crud.get_project_progress(db, project.id)

    return ClientProjectDetail(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        priority=project.priority,
        budget=project.budget,
        amount_paid=project.amount_paid,
        start_date=project.start_date,
        deadline=project.deadline,
        progress_percentage=progress["progress_percentage"],
        is_active=project.is_active,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get(
    "/projects/{project_id}/milestones",
    response_model=list[ClientMilestoneListItem],
    summary="Get project milestones",
)
def get_milestones(project_id: int, db: DbDep, current_user: ClientOnly):
    """Get milestones for a project (active only)."""
    # Verify project belongs to client
    project = client_crud.get_client_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    milestones = client_crud.get_client_milestones(db, project_id)
    return [ClientMilestoneListItem.model_validate(m) for m in milestones]


@router.get(
    "/invoices",
    response_model=list[ClientInvoiceListItem],
    summary="List the authenticated client's invoices",
)
def list_invoices(
    db: DbDep,
    current_user: ClientOnly,
    status: InvoiceStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Invoices belonging to this client, including standalone invoices with no
    project. Staff-facing notes are never included.
    """
    invoices = client_crud.get_client_invoices(
        db, current_user.id, limit=limit, offset=offset, status=status
    )
    return [ClientInvoiceListItem.model_validate(inv) for inv in invoices]


@router.get(
    "/invoices/{invoice_id}",
    response_model=ClientInvoiceDetail,
    summary="Get one of the authenticated client's invoices",
)
def get_invoice(invoice_id: int, db: DbDep, current_user: ClientOnly):
    """404 (not 403) for anything that isn't this client's — same as projects."""
    invoice = client_crud.get_client_invoice_by_id(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    # Issuer details, so the client's copy is a complete VAT invoice.
    invoice.company = settings_crud.get_settings(db)
    return ClientInvoiceDetail.model_validate(invoice)


@router.get(
    "/hosting",
    response_model=list[ClientHostingListItem],
    summary="List the authenticated client's hosting accounts",
)
def list_hosting(db: DbDep, current_user: ClientOnly, include_inactive: bool = False):
    """
    The client's own hosting. The response model carries no `server_notes`, so
    internal provisioning detail cannot leak here.
    """
    accounts = hosting_crud.list_accounts_for_client(
        db, current_user.id, include_inactive=include_inactive
    )
    return [ClientHostingListItem.model_validate(a) for a in accounts]


@router.get(
    "/hosting/{account_id}",
    response_model=ClientHostingDetail,
    summary="Get one of the authenticated client's hosting accounts",
)
def get_hosting(account_id: int, db: DbDep, current_user: ClientOnly):
    """404 (not 403) for anything that isn't this client's — same as projects."""
    account = hosting_crud.get_account_for_client(db, account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Hosting account not found")
    return ClientHostingDetail.model_validate(account)


@router.post(
    "/tickets",
    response_model=ClientTicketDetail,
    status_code=201,
    summary="Open a support ticket",
)
def create_ticket(data: SupportTicketCreate, db: DbDep, current_user: ClientOnly):
    """
    Clients raise their own tickets. Public visitors don't reach this — they use
    the quote form — so the owner is always the authenticated account.
    """
    if data.project_id is not None:
        validate_project_for_ticket(db, data.project_id, current_user.id)

    ticket = support_crud.create_ticket(
        db,
        client_id=current_user.id,
        subject=data.subject,
        description=data.description,
        category=data.category,
        project_id=data.project_id,
    )
    logger.info("client %s opened ticket %s", current_user.id, ticket.id)
    notifications.notify_ticket_created(db, ticket)
    return _client_ticket_detail(ticket)


@router.get(
    "/tickets",
    response_model=list[ClientTicketListItem],
    summary="List the authenticated client's support tickets",
)
def list_tickets(
    db: DbDep,
    current_user: ClientOnly,
    status: TicketStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    tickets = support_crud.list_tickets_for_client(
        db, current_user.id, limit=limit, offset=offset, status=status
    )
    return [ClientTicketListItem.model_validate(t) for t in tickets]


@router.get(
    "/tickets/{ticket_id}",
    response_model=ClientTicketDetail,
    summary="Get one of the authenticated client's tickets with its thread",
)
def get_ticket(ticket_id: int, db: DbDep, current_user: ClientOnly):
    """404 (not 403) for anything that isn't this client's — same as projects."""
    ticket = support_crud.get_ticket_for_client(db, ticket_id, current_user.id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return _client_ticket_detail(ticket)


@router.post(
    "/tickets/{ticket_id}/messages",
    response_model=ClientTicketMessageRead,
    status_code=201,
    summary="Reply on one of the authenticated client's tickets",
)
def add_ticket_message(
    ticket_id: int, data: TicketMessageCreate, db: DbDep, current_user: ClientOnly
):
    ticket = support_crud.get_ticket_for_client(db, ticket_id, current_user.id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    entry = support_crud.add_message(
        db,
        ticket,
        sender_id=current_user.id,
        message=data.message,
        # Hardcoded: `is_internal_note` in the body is ignored here so a client
        # can't post a note that hides from their own view or skips the email.
        is_internal_note=False,
    )
    # The client answering a WAITING_ON_CLIENT ticket puts the ball back with us.
    support_crud.reopen_if_waiting(db, ticket)
    logger.info("client %s replied on ticket %s", current_user.id, ticket_id)

    notifications.notify_ticket_reply_to_staff(db, ticket, entry)
    return ClientTicketMessageRead.model_validate(entry)


@router.get(
    "/domains",
    response_model=list[ClientDomainListItem],
    summary="List the authenticated client's domains",
)
def list_domains(db: DbDep, current_user: ClientOnly, status: DomainStatus | None = None):
    """
    The client's own domains. The response model carries no `notes`, so internal
    remarks cannot leak here.
    """
    domains = domain_crud.list_domains_for_client(db, current_user.id)
    if status is not None:
        domains = [d for d in domains if d.status == status]
    return [ClientDomainListItem.model_validate(d) for d in domains]


@router.get(
    "/domains/{domain_id}",
    response_model=ClientDomainDetail,
    summary="Get one of the authenticated client's domains",
)
def get_domain(domain_id: int, db: DbDep, current_user: ClientOnly):
    """404 (not 403) for anything that isn't this client's — same as projects."""
    domain = domain_crud.get_domain_for_client(db, domain_id, current_user.id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return ClientDomainDetail.model_validate(domain)


@router.get("/quotes", response_model=list[ClientQuoteListItem], summary="List client quotes")
def list_quotes(
    db: DbDep,
    current_user: ClientOnly,
    status: QuoteStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all quote requests associated with the client's email."""
    quotes = client_crud.get_client_quotes(
        db, current_user.email, limit=limit, offset=offset, status=status
    )

    return [ClientQuoteListItem.model_validate(q) for q in quotes]


@router.get(
    "/quotes/{quote_id}",
    response_model=ClientQuoteDetail,
    summary="Get one of the authenticated client's quote requests",
)
def get_quote(quote_id: int, db: DbDep, current_user: ClientOnly):
    """
    The click-through target for a QUOTE_STATUS_CHANGED notification.

    Scoped by email, not client_id: quote requests are public and carry an email
    rather than a user FK, so a client's quotes are the ones submitted with
    their address. 404 for anything else.
    """
    quote = client_crud.get_client_quote_by_id(db, quote_id, current_user.email)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote request not found")

    detail = ClientQuoteDetail.model_validate(quote)

    # Resolve the service name so the client sees "Web Design" rather than an id.
    if quote.service_id is not None:
        service = service_crud.get_by_id(db, quote.service_id)
        detail.service_name = service.name if service else None

    # If this quote became a project, let them click through to it.
    project = project_crud.get_by_quote_request_id(db, quote.id)
    if project is not None and project.client_id == current_user.id:
        detail.converted_project_id = project.id

    return detail
