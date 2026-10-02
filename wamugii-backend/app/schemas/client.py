from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.hosting import BillingCycle, HostingStatus
from app.models.invoice import InvoiceStatus, PaymentMethod
from app.models.project import ProjectPriority, ProjectStatus
from app.models.project_milestone import MilestoneStatus
from app.models.quote_request import QuoteStatus
from app.schemas.quote_request import QuoteAnswerRead
from app.schemas.company_settings import InvoiceCompanyBlock


class ClientUserRead(BaseModel):
    """Basic user info for client dashboard."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class ClientDashboardSummary(BaseModel):
    """Summary statistics for client dashboard."""

    total_projects: int
    active_projects: int
    completed_projects: int
    pending_quotes: int


class ClientProjectListItem(BaseModel):
    """Lightweight project info for dashboard and list."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: ProjectStatus
    priority: ProjectPriority
    deadline: datetime | None
    progress_percentage: float
    created_at: datetime


class ClientProjectDetail(BaseModel):
    """Detailed project info with milestones summary."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: ProjectStatus
    priority: ProjectPriority
    budget: Decimal | None
    amount_paid: Decimal
    start_date: datetime | None
    deadline: datetime | None
    progress_percentage: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClientMilestoneListItem(BaseModel):
    """Milestone info for client view."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: MilestoneStatus
    display_order: int
    due_date: datetime | None
    completed_at: datetime | None


class ClientQuoteListItem(BaseModel):
    """Safe quote info without admin_notes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_title: str
    status: QuoteStatus
    created_at: datetime
    updated_at: datetime


class ClientInvoiceListItem(BaseModel):
    """
    Invoice summary for the client's own view. Deliberately omits `notes`,
    which is staff-facing.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    project_id: int | None
    issue_date: datetime
    due_date: datetime | None
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    status: InvoiceStatus
    created_at: datetime


class ClientInvoiceItemRead(BaseModel):
    """A billed line on the client's own invoice."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class ClientPaymentRead(BaseModel):
    """
    A payment on the client's own invoice. Omits `notes` and `recorded_by` —
    both are internal.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    payment_date: datetime
    method: PaymentMethod
    reference: str | None


class ClientInvoiceDetail(BaseModel):
    """Full invoice detail for the client — still no staff-facing `notes`."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    project_id: int | None
    issue_date: datetime
    due_date: datetime | None
    subtotal: Decimal
    # VAT is a charge the client is actually paying, so the rate and amount are
    # both shown to them — this is not staff-only information like `notes`.
    tax_rate: Decimal | None
    tax: Decimal | None
    discount: Decimal | None
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime
    items: list[ClientInvoiceItemRead] = []
    payments: list[ClientPaymentRead] = []
    # The client needs the issuer's details to have a valid VAT invoice.
    company: InvoiceCompanyBlock | None = None


class ClientQuoteDetail(BaseModel):
    """
    A client's own quote request in full.

    `admin_notes` is not declared here — internal review notes stay internal,
    exactly as ClientQuoteListItem already ensures for the list view.
    `converted_project_id` is filled in when the quote became a project, so the
    client can click through to it.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_title: str
    project_description: str
    service_id: int | None
    service_name: str | None = None
    budget_range: str | None
    preferred_deadline: str | None
    status: QuoteStatus
    created_at: datetime
    updated_at: datetime
    converted_project_id: int | None = None
    # The structured per-service answers, as asked at submit time. Safe for a
    # client to see: these are their own words, not internal review notes.
    answers: list[QuoteAnswerRead] = []


class ClientHostingPlanRead(BaseModel):
    """Plan details a client may see — plans are public anyway."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    features: str
    monthly_price: Decimal
    yearly_price: Decimal


class ClientHostingListItem(BaseModel):
    """
    Hosting summary for the client's own list.

    `server_notes` is not declared on this model or on the detail model below,
    so internal provisioning notes cannot reach a client even if the whole ORM
    row is passed in.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str | None
    status: HostingStatus
    billing_cycle: BillingCycle
    start_date: date | None
    next_billing_date: date | None
    expires_at: date | None
    created_at: datetime
    plan: ClientHostingPlanRead | None = None


class ClientHostingDetail(BaseModel):
    """
    Full hosting detail for the owning client.

    Includes `nameservers` — the client needs those to point their DNS — but
    never `server_notes`, `invoice_id` internals, or any other staff field.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str | None
    nameservers: str | None
    status: HostingStatus
    billing_cycle: BillingCycle
    start_date: date | None
    next_billing_date: date | None
    expires_at: date | None
    created_at: datetime
    updated_at: datetime
    plan: ClientHostingPlanRead | None = None


class ClientActivityItem(BaseModel):
    """Recent activity entry."""

    type: str  # "PROJECT", "MILESTONE", "QUOTE"
    message: str
    created_at: datetime


class ClientDashboardRead(BaseModel):
    """Main client dashboard response."""

    user: ClientUserRead
    summary: ClientDashboardSummary
    recent_projects: list[ClientProjectListItem]
    recent_quotes: list[ClientQuoteListItem]
    recent_activity: list[ClientActivityItem]
