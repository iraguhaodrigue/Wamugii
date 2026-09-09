"""
System-emitted notifications.

Every function here is called from a router *after* the underlying action has
already been committed, and every one routes through `_emit`, which swallows
and logs any failure. That is the contract: a notification problem must never
turn a successful quote/project/invoice/payment into an error for the caller.

There is deliberately no public "create notification" endpoint — notifications
describe things the system did, so letting a client post one would let them
fabricate history.
"""

import logging

from sqlalchemy.orm import Session

from app.crud import notification as notification_crud
from app.crud import user as user_crud
from app.models.invoice import Invoice
from app.models.notification import NotificationType
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.quote_request import QuoteRequest
from app.models.user import User

logger = logging.getLogger(__name__)


def _emit(
    db: Session,
    *,
    user_id: int,
    type: NotificationType,
    title: str,
    message: str,
    related_type: str | None = None,
    related_id: int | None = None,
) -> None:
    """
    Best-effort insert. On failure the session is rolled back (so the request
    can still finish and serialize its response) and the error is logged. The
    triggering action is already committed by this point, so rolling back here
    cannot undo it.
    """
    try:
        notification_crud.create(
            db,
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            related_type=related_type,
            related_id=related_id,
        )
    except Exception:
        db.rollback()
        logger.exception(
            "failed to emit %s notification for user %s (%s %s) — the triggering "
            "action was not affected",
            type.value if hasattr(type, "value") else type,
            user_id,
            related_type,
            related_id,
        )


def _emit_to_staff(db: Session, **kwargs) -> None:
    """Fan out one notification per active ADMIN/STAFF user."""
    try:
        recipient_ids = user_crud.list_active_staff_and_admin_ids(db)
    except Exception:
        db.rollback()
        logger.exception("failed to resolve staff recipients for a notification")
        return
    for user_id in recipient_ids:
        _emit(db, user_id=user_id, **kwargs)


def _client_for_quote(db: Session, quote: QuoteRequest) -> User | None:
    """
    Quote requests are public and carry an email, not a user FK — there may be
    no account behind one. Returns None when nobody can be notified.
    """
    try:
        return user_crud.get_by_email(db, quote.email.lower())
    except Exception:
        db.rollback()
        logger.exception("failed to resolve the client account for quote %s", quote.id)
        return None


# --- quote events -----------------------------------------------------------


def notify_quote_submitted(db: Session, quote: QuoteRequest) -> None:
    _emit_to_staff(
        db,
        type=NotificationType.QUOTE_SUBMITTED,
        title="New quote request",
        message=f"{quote.full_name} submitted a quote request: {quote.project_title}",
        related_type="quote",
        related_id=quote.id,
    )


def notify_quote_status_changed(db: Session, quote: QuoteRequest, old_status: str) -> None:
    client = _client_for_quote(db, quote)
    if client is None:
        # Public quote with no matching account — nobody to notify.
        return
    _emit(
        db,
        user_id=client.id,
        type=NotificationType.QUOTE_STATUS_CHANGED,
        title="Quote request updated",
        message=(
            f"Your quote request '{quote.project_title}' moved from "
            f"{old_status} to {quote.status.value}."
        ),
        related_type="quote",
        related_id=quote.id,
    )


# --- project events ---------------------------------------------------------


def notify_project_created(db: Session, project: Project) -> None:
    _emit(
        db,
        user_id=project.client_id,
        type=NotificationType.PROJECT_CREATED,
        title="Project created",
        message=f"Your project '{project.title}' has been set up.",
        related_type="project",
        related_id=project.id,
    )


def notify_project_status_changed(db: Session, project: Project, old_status: str) -> None:
    _emit(
        db,
        user_id=project.client_id,
        type=NotificationType.PROJECT_STATUS_CHANGED,
        title="Project status updated",
        message=(
            f"'{project.title}' moved from {old_status} to {project.status.value}."
        ),
        related_type="project",
        related_id=project.id,
    )


def notify_milestone_completed(
    db: Session, milestone: ProjectMilestone, project: Project
) -> None:
    _emit(
        db,
        user_id=project.client_id,
        type=NotificationType.MILESTONE_COMPLETED,
        title="Milestone completed",
        message=f"'{milestone.title}' was completed on your project '{project.title}'.",
        # Links to the project: milestones have no page of their own.
        related_type="project",
        related_id=project.id,
    )


def notify_file_uploaded(
    db: Session, project: Project, filename: str, uploaded_by: User
) -> None:
    """Notifies the other side: staff uploads reach the client, and vice versa."""
    if uploaded_by.id == project.client_id:
        _emit_to_staff(
            db,
            type=NotificationType.FILE_UPLOADED,
            title="Client uploaded a file",
            message=f"{uploaded_by.full_name} uploaded '{filename}' to '{project.title}'.",
            related_type="project",
            related_id=project.id,
        )
        return
    _emit(
        db,
        user_id=project.client_id,
        type=NotificationType.FILE_UPLOADED,
        title="New project file",
        message=f"'{filename}' was added to your project '{project.title}'.",
        related_type="project",
        related_id=project.id,
    )


# --- invoice events ---------------------------------------------------------


def notify_invoice_created(db: Session, invoice: Invoice) -> None:
    _emit(
        db,
        user_id=invoice.client_id,
        type=NotificationType.INVOICE_CREATED,
        title="New invoice",
        message=f"Invoice {invoice.invoice_number} for {invoice.total} RWF has been issued.",
        related_type="invoice",
        related_id=invoice.id,
    )


def notify_payment_recorded(db: Session, invoice: Invoice, amount: str) -> None:
    _emit(
        db,
        user_id=invoice.client_id,
        type=NotificationType.PAYMENT_RECORDED,
        title="Payment recorded",
        message=(
            f"A payment of {amount} RWF was recorded against invoice "
            f"{invoice.invoice_number}. Balance due: {invoice.balance_due} RWF."
        ),
        related_type="invoice",
        related_id=invoice.id,
    )
