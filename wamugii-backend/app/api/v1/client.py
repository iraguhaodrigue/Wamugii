import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, DbDep, require_roles
from app.crud import client as client_crud
from app.crud import project_milestone as milestone_crud
from app.models.invoice import InvoiceStatus
from app.models.project import ProjectStatus
from app.models.quote_request import QuoteStatus
from app.models.user import Role, User
from app.schemas.client import (
    ClientActivityItem,
    ClientDashboardRead,
    ClientDashboardSummary,
    ClientInvoiceDetail,
    ClientInvoiceListItem,
    ClientMilestoneListItem,
    ClientProjectDetail,
    ClientProjectListItem,
    ClientQuoteListItem,
    ClientUserRead,
)

router = APIRouter(prefix="/client", tags=["client"])
logger = logging.getLogger(__name__)

ClientOnly = Annotated[User, Depends(require_roles(Role.CLIENT))]


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
    return ClientInvoiceDetail.model_validate(invoice)


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
