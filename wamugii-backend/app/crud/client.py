from datetime import datetime
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.crud import project_milestone as milestone_crud
from app.models.invoice import Invoice, InvoiceStatus, Payment
from app.models.project import Project, ProjectStatus
from app.models.project_milestone import ProjectMilestone, MilestoneStatus
from app.models.quote_request import QuoteRequest, QuoteStatus
from app.models.user import User


def get_client_projects(
    db: Session,
    client_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
    status: ProjectStatus | None = None,
    search: str | None = None,
) -> list[Project]:
    """Get projects for a specific client."""
    query = select(Project).where(
        and_(
            Project.client_id == client_id,
            Project.is_active.is_(True),
        )
    )

    if status is not None:
        query = query.where(Project.status == status)

    if search:
        term = search.lower()
        query = query.where(func.lower(Project.title).contains(term))

    query = query.order_by(Project.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def get_client_project_by_id(
    db: Session, project_id: int, client_id: int
) -> Project | None:
    """Get a project if it belongs to the client."""
    return db.scalar(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.client_id == client_id,
                Project.is_active.is_(True),
            )
        )
    )


def count_client_projects(
    db: Session,
    client_id: int,
    *,
    status: ProjectStatus | None = None,
) -> int:
    """Count projects for a client."""
    query = select(func.count()).select_from(Project).where(
        and_(
            Project.client_id == client_id,
            Project.is_active.is_(True),
        )
    )

    if status is not None:
        query = query.where(Project.status == status)

    return db.scalar(query) or 0


def get_client_quotes(
    db: Session,
    client_email: str,
    *,
    limit: int = 100,
    offset: int = 0,
    status: QuoteStatus | None = None,
) -> list[QuoteRequest]:
    """Get quote requests associated with the client's email."""
    query = select(QuoteRequest).where(
        and_(
            QuoteRequest.email == client_email,
            QuoteRequest.is_active.is_(True),
        )
    )

    if status is not None:
        query = query.where(QuoteRequest.status == status)

    query = query.order_by(QuoteRequest.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def count_client_quotes(
    db: Session,
    client_email: str,
    *,
    status: QuoteStatus | None = None,
) -> int:
    """Count quote requests for a client."""
    query = select(func.count()).select_from(QuoteRequest).where(
        and_(
            QuoteRequest.email == client_email,
            QuoteRequest.is_active.is_(True),
        )
    )

    if status is not None:
        query = query.where(QuoteRequest.status == status)

    return db.scalar(query) or 0


def get_client_milestones(
    db: Session,
    project_id: int,
) -> list[ProjectMilestone]:
    """Get active milestones for a project."""
    query = (
        select(ProjectMilestone)
        .where(
            and_(
                ProjectMilestone.project_id == project_id,
                ProjectMilestone.is_active.is_(True),
            )
        )
        .order_by(ProjectMilestone.display_order.asc())
        .order_by(ProjectMilestone.created_at.asc())
    )
    return list(db.scalars(query).all())


def get_client_invoices(
    db: Session,
    client_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
    status: InvoiceStatus | None = None,
) -> list[Invoice]:
    """
    Invoices belonging to a client. Scoped by client_id exactly like projects —
    note this deliberately does NOT join projects, because a standalone invoice
    has no project and must still be visible to its client.
    """
    query = select(Invoice).where(
        and_(
            Invoice.client_id == client_id,
            Invoice.is_active.is_(True),
        )
    )

    if status is not None:
        query = query.where(Invoice.status == status)

    query = query.order_by(Invoice.issue_date.desc(), Invoice.id.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def get_client_invoice_by_id(db: Session, invoice_id: int, client_id: int) -> Invoice | None:
    """Get an invoice only if it belongs to this client (else None → 404)."""
    return db.scalar(
        select(Invoice).where(
            and_(
                Invoice.id == invoice_id,
                Invoice.client_id == client_id,
                Invoice.is_active.is_(True),
            )
        )
    )


def get_client_invoice_payments(db: Session, invoice_id: int) -> list[Payment]:
    """Payment history for an invoice the caller has already been scoped to."""
    return list(
        db.scalars(
            select(Payment)
            .where(and_(Payment.invoice_id == invoice_id, Payment.is_active.is_(True)))
            .order_by(Payment.payment_date.asc(), Payment.id.asc())
        ).all()
    )


def get_dashboard_summary(db: Session, client_id: int, client_email: str) -> dict:
    """Calculate dashboard summary statistics."""
    total_projects = count_client_projects(db, client_id)
    active_projects = count_client_projects(db, client_id, status=ProjectStatus.IN_PROGRESS)
    completed_projects = count_client_projects(db, client_id, status=ProjectStatus.COMPLETED)
    pending_quotes = count_client_quotes(db, client_email, status=QuoteStatus.NEW)

    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "pending_quotes": pending_quotes,
    }


def get_recent_projects(db: Session, client_id: int, limit: int = 5) -> list[Project]:
    """Get recent projects for client."""
    return get_client_projects(db, client_id, limit=limit, offset=0)


def get_recent_quotes(db: Session, client_email: str, limit: int = 5) -> list[QuoteRequest]:
    """Get recent quotes for client."""
    return get_client_quotes(db, client_email, limit=limit, offset=0)


def generate_recent_activity(
    db: Session, client_id: int, client_email: str, limit: int = 10
) -> list[dict]:
    """Generate recent activity from existing data."""
    activities = []

    # Get recent projects
    recent_projects = get_recent_projects(db, client_id, limit=limit)
    for project in recent_projects:
        activities.append(
            {
                "type": "PROJECT",
                "message": f"Project '{project.title}' created",
                "created_at": project.created_at,
            }
        )

    # Get recent quotes
    recent_quotes = get_recent_quotes(db, client_email, limit=limit)
    for quote in recent_quotes:
        activities.append(
            {
                "type": "QUOTE",
                "message": f"Quote request '{quote.project_title}' submitted",
                "created_at": quote.created_at,
            }
        )

    # Get recent milestone completions
    query = (
        select(ProjectMilestone)
        .join(Project)
        .where(
            and_(
                Project.client_id == client_id,
                ProjectMilestone.status == MilestoneStatus.COMPLETED,
                ProjectMilestone.is_active.is_(True),
            )
        )
        .order_by(ProjectMilestone.updated_at.desc())
        .limit(limit)
    )
    recent_milestones = list(db.scalars(query).all())
    for milestone in recent_milestones:
        activities.append(
            {
                "type": "MILESTONE",
                "message": f"Milestone '{milestone.title}' completed",
                "created_at": milestone.updated_at,
            }
        )

    # Sort by date descending and limit
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    return activities[:limit]
