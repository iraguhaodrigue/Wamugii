import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, enum.Enum):
    MOBILE_MONEY = "MOBILE_MONEY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH = "CASH"
    OTHER = "OTHER"


class Invoice(Base):
    """
    A bill issued to a client. `project_id` is nullable on purpose: a standalone
    invoice (an electronics sale, a one-off consultation) is fully valid and no
    invoice logic may assume a project exists. `client_id` is always required.

    Money is stored as Numeric(12, 2) to match projects.budget/amount_paid, and
    surfaces as decimal strings through the Pydantic schemas. `total` and
    `amount_paid` are always computed server-side — see crud/invoice.py.
    """

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True, index=True
    )

    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    tax: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def balance_due(self) -> Decimal:
        """
        Always derived, never stored — so it cannot drift from the amounts and
        cannot be supplied by a caller. Payments that would exceed `total` are
        rejected in crud.record_payment, so this never goes negative.
        """
        return (self.total or Decimal("0")) - (self.amount_paid or Decimal("0"))

    client = relationship("User")
    project = relationship("Project")
    items = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceItem.id"
    )
    payments = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan", order_by="Payment.id"
    )


class InvoiceItem(Base):
    """
    A single billed line. `line_total` is derived (quantity * unit_price) and
    recomputed server-side on every write — it is never taken from the client.
    """

    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)

    description: Mapped[str] = mapped_column(String(500))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    invoice = relationship("Invoice", back_populates="items")


class Payment(Base):
    """
    A manually recorded payment against an invoice. This records that money was
    received out-of-band (mobile money, bank transfer, cash) — there is no
    online payment processing here, and no card data is stored: `reference` is
    a free-text human reference such as a transaction ID, never a card number.
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), index=True)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    recorded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    invoice = relationship("Invoice", back_populates="payments")
