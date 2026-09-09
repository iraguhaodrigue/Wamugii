from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.invoice import InvoiceStatus, PaymentMethod

# Statuses a client of the API may set directly. PAID / PARTIALLY_PAID / OVERDUE
# are derived from the money and the due date, so accepting them from the
# request would let the caller assert a state the amounts contradict.
SETTABLE_STATUSES = {InvoiceStatus.DRAFT, InvoiceStatus.SENT, InvoiceStatus.CANCELLED}


class InvoiceItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    # line_total is intentionally absent — it is computed as quantity * unit_price.


class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class InvoiceCreate(BaseModel):
    client_id: int
    project_id: int | None = None
    issue_date: datetime | None = None
    due_date: datetime | None = None
    # Ignored when `items` is supplied — subtotal is then the sum of the lines.
    subtotal: Decimal = Field(default=Decimal("0"), ge=0)
    tax: Decimal | None = Field(default=None, ge=0)
    discount: Decimal | None = Field(default=None, ge=0)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    notes: str | None = None
    items: list[InvoiceItemCreate] | None = None
    # total / amount_paid are intentionally absent — server-computed.


class InvoiceUpdate(BaseModel):
    project_id: int | None = None
    issue_date: datetime | None = None
    due_date: datetime | None = None
    subtotal: Decimal | None = Field(default=None, ge=0)
    tax: Decimal | None = Field(default=None, ge=0)
    discount: Decimal | None = Field(default=None, ge=0)
    status: InvoiceStatus | None = None
    notes: str | None = None
    # Supplying `items` replaces the whole set and recomputes subtotal.
    items: list[InvoiceItemCreate] | None = None


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    payment_date: datetime | None = None
    method: PaymentMethod
    # Free-text human reference (e.g. a mobile-money transaction ID). Never card data.
    reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    payment_date: datetime
    method: PaymentMethod
    reference: str | None
    notes: str | None
    recorded_by: int
    created_at: datetime


class InvoiceRead(BaseModel):
    """Full staff-facing invoice, including internal notes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    client_id: int
    project_id: int | None
    issue_date: datetime
    due_date: datetime | None
    subtotal: Decimal
    tax: Decimal | None
    discount: Decimal | None
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    status: InvoiceStatus
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list[InvoiceItemRead] = []
    payments: list[PaymentRead] = []


class InvoiceListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    client_id: int
    project_id: int | None
    issue_date: datetime
    due_date: datetime | None
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    status: InvoiceStatus
    is_active: bool
    created_at: datetime
