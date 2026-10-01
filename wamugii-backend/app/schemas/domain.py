from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.domain import DEFAULT_REGISTRAR, DomainStatus

# Statuses an admin/staff member may set directly. EXPIRED is absent for the
# same reason as on hosting: it describes a date passing, not a decision.
SETTABLE_STATUSES = {
    DomainStatus.PENDING,
    DomainStatus.ACTIVE,
    DomainStatus.CANCELLED,
}


class DomainCreate(BaseModel):
    client_id: int
    hosting_account_id: int | None = None
    domain_name: str = Field(min_length=1, max_length=255)
    registrar: str = Field(default=DEFAULT_REGISTRAR, max_length=100)
    registration_fee: Decimal = Field(default=Decimal("0"), ge=0)
    service_fee: Decimal | None = Field(default=None, ge=0)
    status: DomainStatus = DomainStatus.PENDING
    registered_date: date | None = None
    expires_at: date | None = None
    auto_renew: bool = False
    nameservers: str | None = None
    notes: str | None = None
    invoice_id: int | None = None


class DomainUpdate(BaseModel):
    hosting_account_id: int | None = None
    domain_name: str | None = Field(default=None, min_length=1, max_length=255)
    registrar: str | None = Field(default=None, max_length=100)
    registration_fee: Decimal | None = Field(default=None, ge=0)
    service_fee: Decimal | None = Field(default=None, ge=0)
    status: DomainStatus | None = None
    registered_date: date | None = None
    expires_at: date | None = None
    auto_renew: bool | None = None
    nameservers: str | None = None
    notes: str | None = None
    invoice_id: int | None = None


class DomainRead(BaseModel):
    """Full staff view, including the internal notes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    hosting_account_id: int | None
    domain_name: str
    registrar: str
    registration_fee: Decimal
    service_fee: Decimal | None
    total_fee: Decimal
    status: DomainStatus
    registered_date: date | None
    expires_at: date | None
    auto_renew: bool
    nameservers: str | None
    notes: str | None
    invoice_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DomainListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    hosting_account_id: int | None
    domain_name: str
    registrar: str
    status: DomainStatus
    expires_at: date | None
    is_active: bool
    created_at: datetime


# --- client-facing ----------------------------------------------------------


class ClientDomainListItem(BaseModel):
    """
    The client's own domain list. `notes` is not declared here or on the detail
    model below, so internal remarks cannot leak even if the ORM row is passed
    in whole.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    domain_name: str
    registrar: str
    status: DomainStatus
    registered_date: date | None
    expires_at: date | None
    auto_renew: bool
    created_at: datetime


class ClientDomainDetail(BaseModel):
    """
    Full detail for the owning client — including nameservers (they may need
    them) and what they were charged, but never internal notes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    hosting_account_id: int | None
    domain_name: str
    registrar: str
    registration_fee: Decimal
    service_fee: Decimal | None
    total_fee: Decimal
    status: DomainStatus
    registered_date: date | None
    expires_at: date | None
    auto_renew: bool
    nameservers: str | None
    created_at: datetime
    updated_at: datetime
