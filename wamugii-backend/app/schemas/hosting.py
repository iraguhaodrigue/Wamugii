from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.hosting import BillingCycle, HostingStatus

# Statuses an admin/staff member may set directly. EXPIRED is deliberately
# absent: it describes a date passing, not a decision, so it belongs to a sweep
# over expires_at rather than a dropdown.
SETTABLE_STATUSES = {
    HostingStatus.PENDING,
    HostingStatus.ACTIVE,
    HostingStatus.SUSPENDED,
    HostingStatus.CANCELLED,
}


# --- plans ------------------------------------------------------------------


class HostingPlanBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    features: str = ""
    monthly_price: Decimal = Field(default=Decimal("0"), ge=0)
    yearly_price: Decimal = Field(default=Decimal("0"), ge=0)
    display_order: int = 0


class HostingPlanCreate(HostingPlanBase):
    is_active: bool = True


class HostingPlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    features: str | None = None
    monthly_price: Decimal | None = Field(default=None, ge=0)
    yearly_price: Decimal | None = Field(default=None, ge=0)
    display_order: int | None = None
    is_active: bool | None = None


class HostingPlanRead(BaseModel):
    """Plans are public — there is nothing internal on them."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    features: str
    monthly_price: Decimal
    yearly_price: Decimal
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


# --- accounts (staff-facing) ------------------------------------------------


class HostingAccountCreate(BaseModel):
    client_id: int
    plan_id: int
    domain: str | None = Field(default=None, max_length=255)
    nameservers: str | None = None
    server_notes: str | None = None
    status: HostingStatus = HostingStatus.PENDING
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    start_date: date | None = None
    expires_at: date | None = None
    invoice_id: int | None = None
    # next_billing_date is intentionally absent — derived from start_date and
    # billing_cycle by crud.hosting.create_account.


class HostingAccountUpdate(BaseModel):
    plan_id: int | None = None
    domain: str | None = Field(default=None, max_length=255)
    nameservers: str | None = None
    server_notes: str | None = None
    status: HostingStatus | None = None
    billing_cycle: BillingCycle | None = None
    start_date: date | None = None
    next_billing_date: date | None = None
    expires_at: date | None = None
    invoice_id: int | None = None


class HostingAccountRead(BaseModel):
    """Full staff view, including the internal server notes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    plan_id: int
    domain: str | None
    nameservers: str | None
    server_notes: str | None
    status: HostingStatus
    billing_cycle: BillingCycle
    start_date: date | None
    next_billing_date: date | None
    expires_at: date | None
    invoice_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    plan: HostingPlanRead | None = None


class HostingAccountListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    plan_id: int
    domain: str | None
    status: HostingStatus
    billing_cycle: BillingCycle
    next_billing_date: date | None
    expires_at: date | None
    is_active: bool
    created_at: datetime


class NextBillingPreview(BaseModel):
    """What the create form shows before saving."""

    start_date: date
    billing_cycle: BillingCycle
    next_billing_date: date
