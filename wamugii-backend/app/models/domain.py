import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

DEFAULT_REGISTRAR = "Namecheap"


class DomainStatus(str, enum.Enum):
    PENDING = "PENDING"      # requested / paid for, not yet registered
    ACTIVE = "ACTIVE"        # registered and live
    EXPIRED = "EXPIRED"      # past expires_at
    CANCELLED = "CANCELLED"  # not renewed / dropped


class Domain(Base):
    """
    A domain WAMUGII registered on a client's behalf.

    Two money columns because they are different things: `registration_fee` is
    what the registrar charged, `service_fee` is WAMUGII's charge for handling
    it. Keeping them apart means an invoice can show the pass-through cost and
    the service separately, and `service_fee` can legitimately be zero.

    `hosting_account_id` is optional — a domain can exist without hosting — and
    when set it must belong to the same client, the rule invoices and tickets
    already enforce.

    `notes` is internal and absent from every client-facing schema.
    `auto_renew` is informational only: renewal is a manual admin action, so
    nothing in this module acts on the flag.
    """

    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    hosting_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("hosting_accounts.id"), nullable=True, index=True
    )

    domain_name: Mapped[str] = mapped_column(String(255), index=True)
    registrar: Mapped[str] = mapped_column(String(100), default=DEFAULT_REGISTRAR)

    registration_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    service_fee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    status: Mapped[DomainStatus] = mapped_column(
        Enum(DomainStatus), default=DomainStatus.PENDING, index=True
    )

    registered_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)

    nameservers: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Internal only — never serialized to a client.
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id"), nullable=True, index=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client = relationship("User")
    hosting_account = relationship("HostingAccount")
    invoice = relationship("Invoice")

    @property
    def total_fee(self) -> Decimal:
        """
        Registration plus service — what an invoice for this domain comes to.
        Derived so it can't drift from the two parts.
        """
        return (self.registration_fee or Decimal("0")) + (self.service_fee or Decimal("0"))
