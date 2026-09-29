from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# The settings row always has this id — see crud/company_settings.get_settings,
# which creates it on first read.
SETTINGS_ID = 1

DEFAULT_COMPANY_NAME = "WAMUGII TECH SOLUTIONS"
DEFAULT_SLOGAN = "We Build. We Innovate. We Empower."


class CompanySettings(Base):
    """
    WAMUGII's own company profile — a singleton: exactly one row, id 1, created
    on first read. No `is_active` and no delete endpoint, because there is
    nothing here to soft-delete; the row is configuration, not a record.

    `tin` is the RRA Tax Identification Number printed on VAT invoices, and
    `notification_email` optionally redirects new-quote emails to one inbox
    instead of every staff member — both are internal and are never exposed by
    the public settings endpoint.
    """

    __tablename__ = "company_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    company_name: Mapped[str] = mapped_column(String(255), default=DEFAULT_COMPANY_NAME)
    slogan: Mapped[str] = mapped_column(String(255), default=DEFAULT_SLOGAN)

    tin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    notification_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
