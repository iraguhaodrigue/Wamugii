from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, Payment
from app.schemas.invoice import InvoiceCreate, InvoiceItemCreate, InvoiceUpdate, PaymentCreate

ZERO = Decimal("0.00")

# Statuses that mean "this invoice still owes money" — used by the list filter
# and the dashboard's outstanding figure.
OUTSTANDING_STATUSES = (
    InvoiceStatus.SENT,
    InvoiceStatus.PARTIALLY_PAID,
    InvoiceStatus.OVERDUE,
)


def _quantize(value: Decimal) -> Decimal:
    """Money is 2dp everywhere; keep arithmetic results on that grid."""
    return Decimal(value).quantize(Decimal("0.01"))


def _quantize_tax(value: Decimal) -> Decimal:
    """
    2dp with half-up rounding, which is what RRA expects on a VAT amount: half a
    cent always rounds up (180.045 -> 180.05), never to the nearest even digit
    like Python's default ROUND_HALF_EVEN would (-> 180.04).

    Deliberately scoped to tax only — see compute_tax. The rest of the money
    math keeps `_quantize`, which is safe there because subtotal/tax/discount
    are already exact 2dp values by the time `compute_total` adds them up, so
    no rounding decision actually occurs.
    """
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_tax(
    subtotal: Decimal,
    tax_rate: Decimal | None,
    manual_tax: Decimal | None,
) -> Decimal | None:
    """
    The one place a tax amount is decided.

    With a `tax_rate` set the amount is derived — subtotal × rate / 100, rounded
    half-up to 2dp — and any tax amount supplied by the caller is ignored
    outright. That keeps a VAT invoice honest: the charge always matches the
    rate printed next to it.

    With `tax_rate` NULL this is the pre-VAT behaviour untouched: whatever
    amount was passed in stands, including None.

    Both branches round half-up: a tax figure is a tax figure whether it was
    derived from a rate or typed in by hand, and RRA expects the same treatment
    either way.
    """
    if tax_rate is not None:
        return _quantize_tax(Decimal(subtotal or 0) * Decimal(tax_rate) / Decimal(100))
    return _quantize_tax(Decimal(manual_tax)) if manual_tax is not None else None


def compute_total(subtotal: Decimal, tax: Decimal | None, discount: Decimal | None) -> Decimal:
    """total = subtotal + tax - discount, floored at zero."""
    total = Decimal(subtotal or 0) - Decimal(discount or 0) + Decimal(tax or 0)
    return _quantize(max(total, ZERO))


def derive_status(
    *,
    total: Decimal,
    amount_paid: Decimal,
    current_status: InvoiceStatus,
    due_date: datetime | None,
    now: datetime | None = None,
) -> InvoiceStatus:
    """
    Single source of truth for invoice status.

    CANCELLED is terminal and always wins. Otherwise the money decides: fully
    paid is PAID, part-paid is PARTIALLY_PAID. Only when nothing has been paid
    does the workflow status (DRAFT/SENT) stand, and a SENT invoice past its
    due date reads as OVERDUE.
    """
    if current_status == InvoiceStatus.CANCELLED:
        return InvoiceStatus.CANCELLED

    paid = Decimal(amount_paid or 0)
    owed = Decimal(total or 0)

    if owed > ZERO and paid >= owed:
        return InvoiceStatus.PAID
    if paid > ZERO:
        return InvoiceStatus.PARTIALLY_PAID

    # Nothing paid yet — keep the workflow status, but let an unpaid SENT
    # invoice fall to OVERDUE once its due date has passed.
    base = current_status if current_status in (InvoiceStatus.DRAFT, InvoiceStatus.SENT) else InvoiceStatus.SENT
    if base == InvoiceStatus.SENT and due_date is not None:
        moment = now or datetime.now(timezone.utc)
        due = due_date if due_date.tzinfo else due_date.replace(tzinfo=timezone.utc)
        if due < moment:
            return InvoiceStatus.OVERDUE
    return base


def _sum_items(items: list[InvoiceItemCreate]) -> Decimal:
    return _quantize(sum((Decimal(i.quantity) * Decimal(i.unit_price) for i in items), ZERO))


def _build_items(items: list[InvoiceItemCreate]) -> list[InvoiceItem]:
    return [
        InvoiceItem(
            description=item.description,
            quantity=_quantize(Decimal(item.quantity)),
            unit_price=_quantize(Decimal(item.unit_price)),
            line_total=_quantize(Decimal(item.quantity) * Decimal(item.unit_price)),
        )
        for item in items
    ]


def generate_invoice_number(db: Session, *, year: int | None = None) -> str:
    """
    Human-readable sequential number, e.g. WAM-2026-0001, scoped per year.

    Derived from the highest existing number for the year rather than a row
    count, so soft-deleted invoices never cause a collision. The column is
    UNIQUE and `create` retries on IntegrityError, which covers the race
    between two concurrent creates.
    """
    year = year or datetime.now(timezone.utc).year
    prefix = f"WAM-{year}-"
    highest = db.scalar(
        select(func.max(Invoice.invoice_number)).where(Invoice.invoice_number.like(f"{prefix}%"))
    )
    next_seq = 1
    if highest:
        try:
            next_seq = int(highest.rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):  # pragma: no cover - defensive
            next_seq = 1
    return f"{prefix}{next_seq:04d}"


def get_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return db.get(Invoice, invoice_id)


def list_invoices(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    status: InvoiceStatus | None = None,
    client_id: int | None = None,
    project_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[Invoice]:
    query = select(Invoice)
    if not include_inactive:
        query = query.where(Invoice.is_active.is_(True))
    if status is not None:
        query = query.where(Invoice.status == status)
    if client_id is not None:
        query = query.where(Invoice.client_id == client_id)
    if project_id is not None:
        query = query.where(Invoice.project_id == project_id)
    if search:
        query = query.where(func.lower(Invoice.invoice_number).contains(search.lower()))
    query = query.order_by(Invoice.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def create(db: Session, data: InvoiceCreate) -> Invoice:
    items = data.items or []
    subtotal = _sum_items(items) if items else _quantize(Decimal(data.subtotal or 0))
    tax_rate = _quantize(Decimal(data.tax_rate)) if data.tax_rate is not None else None
    # Derived when a rate is set, so data.tax is deliberately not trusted here.
    tax = compute_tax(subtotal, tax_rate, data.tax)
    total = compute_total(subtotal, tax, data.discount)
    issue_date = data.issue_date or datetime.now(timezone.utc)
    status = derive_status(
        total=total,
        amount_paid=ZERO,
        current_status=data.status,
        due_date=data.due_date,
    )

    # Retry covers the (rare) race where two creates pick the same number
    # between the SELECT MAX and the INSERT; the UNIQUE index is the guard.
    for attempt in range(5):
        invoice = Invoice(
            invoice_number=generate_invoice_number(db),
            client_id=data.client_id,
            project_id=data.project_id,
            issue_date=issue_date,
            due_date=data.due_date,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax=tax,
            discount=_quantize(Decimal(data.discount)) if data.discount is not None else None,
            total=total,
            amount_paid=ZERO,
            status=status,
            notes=data.notes,
            items=_build_items(items),
        )
        db.add(invoice)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if attempt == 4:
                raise
            continue
        db.refresh(invoice)
        return invoice
    raise RuntimeError("could not allocate an invoice number")  # pragma: no cover


def update(db: Session, invoice: Invoice, data: InvoiceUpdate) -> Invoice:
    updates = data.model_dump(exclude_unset=True)
    new_items = updates.pop("items", None)

    for field, value in updates.items():
        if field in ("tax", "discount", "subtotal", "tax_rate") and value is not None:
            value = _quantize(Decimal(value))
        setattr(invoice, field, value)

    # Supplying items replaces the whole set; subtotal then follows the lines.
    if new_items is not None:
        parsed = [InvoiceItemCreate(**item) for item in new_items]
        invoice.items = _build_items(parsed)
        invoice.subtotal = _sum_items(parsed)

    # Runs after the subtotal is final, so editing line items re-derives VAT.
    # On a rated invoice this overwrites any `tax` the caller sent; with no rate
    # it leaves the manual amount exactly as set above.
    invoice.tax = compute_tax(invoice.subtotal, invoice.tax_rate, invoice.tax)

    invoice.total = compute_total(invoice.subtotal, invoice.tax, invoice.discount)
    invoice.status = derive_status(
        total=invoice.total,
        amount_paid=invoice.amount_paid,
        current_status=invoice.status,
        due_date=invoice.due_date,
    )
    db.commit()
    db.refresh(invoice)
    return invoice


def deactivate(db: Session, invoice: Invoice) -> Invoice:
    invoice.is_active = False
    db.commit()
    db.refresh(invoice)
    return invoice


def record_payment(db: Session, invoice: Invoice, data: PaymentCreate, recorded_by: int) -> Payment:
    """
    Append a payment row, then recompute amount_paid from the payment rows so
    the invoice total can never drift from its payment history.
    """
    payment = Payment(
        invoice_id=invoice.id,
        amount=_quantize(Decimal(data.amount)),
        payment_date=data.payment_date or datetime.now(timezone.utc),
        method=data.method,
        reference=data.reference,
        notes=data.notes,
        recorded_by=recorded_by,
    )
    db.add(payment)
    db.flush()

    invoice.amount_paid = sum_payments(db, invoice.id)
    invoice.status = derive_status(
        total=invoice.total,
        amount_paid=invoice.amount_paid,
        current_status=invoice.status,
        due_date=invoice.due_date,
    )
    db.commit()
    db.refresh(payment)
    return payment


def sum_payments(db: Session, invoice_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.invoice_id == invoice_id, Payment.is_active.is_(True)
        )
    )
    return _quantize(Decimal(total or 0))


def list_payments(db: Session, invoice_id: int) -> list[Payment]:
    return list(
        db.scalars(
            select(Payment)
            .where(Payment.invoice_id == invoice_id, Payment.is_active.is_(True))
            .order_by(Payment.payment_date.asc(), Payment.id.asc())
        ).all()
    )


# --- dashboard aggregates: COUNT/SUM in SQL, never row loading -------------


def count_outstanding(db: Session) -> int:
    """Active invoices that still owe money."""
    return (
        db.scalar(
            select(func.count())
            .select_from(Invoice)
            .where(Invoice.status.in_(OUTSTANDING_STATUSES), Invoice.is_active.is_(True))
        )
        or 0
    )


def sum_outstanding(db: Session) -> Decimal:
    """Total unpaid money across active invoices, summed in SQL."""
    total = db.scalar(
        select(func.coalesce(func.sum(Invoice.total - Invoice.amount_paid), 0)).where(
            Invoice.status.in_(OUTSTANDING_STATUSES), Invoice.is_active.is_(True)
        )
    )
    return _quantize(Decimal(total or 0))
