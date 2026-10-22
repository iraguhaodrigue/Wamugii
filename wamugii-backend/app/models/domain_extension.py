from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# The default per-year markup, in RWF. A column default rather than a hardcoded
# constant so an admin editing an extension sees it as the starting value.
DEFAULT_MARGIN = Decimal("5000.00")


class DomainExtension(Base):
    """
    An admin-managed per-TLD price list.

    `cost_price` is what the registrar charges WAMUGII per year; `margin` is
    the flat markup. The client price is `cost_price + margin`, derived at
    read time and never stored -- that way changing the cost or the margin
    updates every quote the next time it is served without an UPDATE.

    `extension` carries the leading dot (`.com`) rather than the bare label,
    so there is one normalised form across the schema and the UI.
    """

    __tablename__ = "domain_extensions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Unique: there is one per extension, matched exactly on write.
    extension: Mapped[str] = mapped_column(String(16), unique=True, index=True)

    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    margin: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=DEFAULT_MARGIN)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def client_price(self) -> Decimal:
        """What the client is billed per year. Derived, so it can't drift."""
        return (self.cost_price or Decimal("0")) + (self.margin or Decimal("0"))
