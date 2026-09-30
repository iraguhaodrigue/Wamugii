import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HostingStatus(str, enum.Enum):
    PENDING = "PENDING"      # requested / created, not yet provisioned
    ACTIVE = "ACTIVE"        # live on the server
    SUSPENDED = "SUSPENDED"  # payment overdue or admin action
    EXPIRED = "EXPIRED"      # past expires_at
    CANCELLED = "CANCELLED"  # terminated


class BillingCycle(str, enum.Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class HostingPlan(Base):
    """
    An admin-defined hosting tier clients subscribe to.

    `features` is a single plain string rather than a related table — the plans
    are a short marketing list rendered as-is on the pricing page, and giving
    each bullet its own row would buy nothing. Prices are Numeric(12, 2) to
    match every other money column and surface as decimal strings.
    """

    __tablename__ = "hosting_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    features: Mapped[str] = mapped_column(Text, default="")

    monthly_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    yearly_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    accounts = relationship("HostingAccount", back_populates="plan")


class HostingAccount(Base):
    """
    One client's hosting subscription.

    Billing runs through the existing invoicing module rather than anything new:
    `invoice_id` points at the most recent invoice an admin raised for this
    account, and payment is recorded through the existing payment endpoints.
    Nothing here generates an invoice automatically.

    `server_notes` is strictly internal (which droplet, which control-panel
    user) and is absent from every client-facing schema — see
    schemas/client.ClientHostingDetail.
    """

    __tablename__ = "hosting_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("hosting_plans.id"), index=True)

    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    nameservers: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Internal only — never serialized to a client.
    server_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[HostingStatus] = mapped_column(
        Enum(HostingStatus), default=HostingStatus.PENDING, index=True
    )
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        Enum(BillingCycle), default=BillingCycle.MONTHLY
    )

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_billing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id"), nullable=True, index=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client = relationship("User")
    plan = relationship("HostingPlan", back_populates="accounts")
    invoice = relationship("Invoice")
