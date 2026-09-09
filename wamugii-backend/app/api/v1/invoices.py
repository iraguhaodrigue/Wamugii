import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.crud import invoice as invoice_crud
from app.crud import project as project_crud
from app.crud import user as user_crud
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import Role, User
from app.schemas.invoice import (
    SETTABLE_STATUSES,
    InvoiceCreate,
    InvoiceListItem,
    InvoiceRead,
    InvoiceUpdate,
    PaymentCreate,
    PaymentRead,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]

# An invoice in one of these states is settled or void: editing it would
# rewrite a financial record the client has already been given. Only `notes`
# (staff-facing, non-financial) stays editable.
LOCKED_STATUSES = (InvoiceStatus.PAID, InvoiceStatus.CANCELLED)


def validate_client_for_invoice(db: Session, client_id: int) -> None:
    client = user_crud.get_by_id(db, client_id)
    if not client or not client.is_active or client.role != Role.CLIENT:
        raise HTTPException(
            status_code=422,
            detail="client_id must reference an active user with the CLIENT role",
        )


def validate_project_for_invoice(db: Session, project_id: int, client_id: int) -> None:
    """
    A linked project must exist, be active, and belong to the same client being
    billed. Invoices with no project skip this entirely — standalone invoices
    are first-class.
    """
    project = project_crud.get_by_id(db, project_id)
    if not project or not project.is_active:
        raise HTTPException(
            status_code=422, detail="project_id does not reference an active project"
        )
    if project.client_id != client_id:
        raise HTTPException(
            status_code=422,
            detail="project_id belongs to a different client than client_id",
        )


def validate_settable_status(status: InvoiceStatus | None) -> None:
    if status is not None and status not in SETTABLE_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=(
                "status is derived from the amounts and cannot be set directly; "
                f"settable values are {sorted(s.value for s in SETTABLE_STATUSES)}"
            ),
        )


@router.post("", response_model=InvoiceRead, status_code=201, summary="Create an invoice (ADMIN or STAFF)")
def create_invoice(data: InvoiceCreate, db: DbDep, current_user: StaffOrAdmin):
    validate_client_for_invoice(db, data.client_id)
    if data.project_id is not None:
        validate_project_for_invoice(db, data.project_id, data.client_id)
    validate_settable_status(data.status)

    invoice = invoice_crud.create(db, data)
    logger.info(
        "staff %s created invoice %s (%s) for client %s",
        current_user.id,
        invoice.id,
        invoice.invoice_number,
        data.client_id,
    )
    return invoice


@router.get("", response_model=list[InvoiceListItem], summary="List invoices (ADMIN or STAFF)")
def list_invoices(
    db: DbDep,
    current_user: StaffOrAdmin,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: InvoiceStatus | None = None,
    client_id: int | None = None,
    project_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    return invoice_crud.list_invoices(
        db,
        limit=limit,
        offset=offset,
        status=status,
        client_id=client_id,
        project_id=project_id,
        search=search,
        include_inactive=include_inactive,
    )


@router.get("/{invoice_id}", response_model=InvoiceRead, summary="Get an invoice (ADMIN or STAFF)")
def get_invoice(invoice_id: int, db: DbDep, current_user: StaffOrAdmin):
    invoice = invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceRead, summary="Update an invoice (ADMIN or STAFF)")
def update_invoice(invoice_id: int, data: InvoiceUpdate, db: DbDep, current_user: StaffOrAdmin):
    invoice = invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    fields = set(data.model_fields_set)
    if invoice.status in LOCKED_STATUSES and fields - {"notes"}:
        raise HTTPException(
            status_code=409,
            detail=(
                f"A {invoice.status.value} invoice cannot be edited; only `notes` may be changed. "
                "Issue a new invoice instead."
            ),
        )

    validate_settable_status(data.status)

    client_id = invoice.client_id
    if "project_id" in fields and data.project_id is not None:
        validate_project_for_invoice(db, data.project_id, client_id)

    updated = invoice_crud.update(db, invoice, data)
    logger.info(
        "staff %s updated invoice %s: %s",
        current_user.id,
        invoice_id,
        data.model_dump(exclude_unset=True),
    )
    return updated


@router.delete("/{invoice_id}", response_model=InvoiceRead, summary="Deactivate an invoice (ADMIN only, soft delete)")
def deactivate_invoice(invoice_id: int, db: DbDep, current_user: AdminOnly):
    invoice = invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    updated = invoice_crud.deactivate(db, invoice)
    logger.info("admin %s deactivated invoice %s", current_user.id, invoice_id)
    return updated


@router.post(
    "/{invoice_id}/payments",
    response_model=PaymentRead,
    status_code=201,
    summary="Record a manual payment against an invoice (ADMIN or STAFF)",
)
def record_payment(invoice_id: int, data: PaymentCreate, db: DbDep, current_user: StaffOrAdmin):
    """
    Records money already received out-of-band (mobile money, bank transfer,
    cash). This is bookkeeping only — no payment is processed here.
    """
    invoice: Invoice | None = invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.status == InvoiceStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Cannot record a payment against a CANCELLED invoice")
    if invoice.status == InvoiceStatus.PAID:
        raise HTTPException(status_code=409, detail="This invoice is already paid in full")

    if data.amount > invoice.balance_due:
        raise HTTPException(
            status_code=422,
            detail=f"Payment exceeds the outstanding balance of {invoice.balance_due}",
        )

    payment = invoice_crud.record_payment(db, invoice, data, recorded_by=current_user.id)
    logger.info(
        "staff %s recorded payment %s of %s on invoice %s",
        current_user.id,
        payment.id,
        payment.amount,
        invoice_id,
    )
    return payment


@router.get(
    "/{invoice_id}/payments",
    response_model=list[PaymentRead],
    summary="List payments on an invoice (ADMIN or STAFF)",
)
def list_payments(invoice_id: int, db: DbDep, current_user: StaffOrAdmin):
    invoice = invoice_crud.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice_crud.list_payments(db, invoice_id)
