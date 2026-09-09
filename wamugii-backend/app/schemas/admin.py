from decimal import Decimal

from pydantic import BaseModel


class UserStats(BaseModel):
    total: int
    clients: int
    staff: int
    admins: int


class ServiceStats(BaseModel):
    total: int
    active: int


class ProjectStats(BaseModel):
    total: int = 0
    active: int = 0


class QuoteStats(BaseModel):
    pending: int = 0


class InvoiceStats(BaseModel):
    # `pending` predates the invoices module and keeps its name/meaning:
    # invoices still awaiting full payment (SENT / PARTIALLY_PAID / OVERDUE).
    pending: int = 0
    # Added with the invoices module — there was no slot for the money owed.
    # Decimal string (e.g. "1500.00") to match every other money field.
    outstanding: Decimal = Decimal("0.00")


class HostingStats(BaseModel):
    active: int = 0


class StoreStats(BaseModel):
    products: int = 0
    pending_orders: int = 0


class SupportStats(BaseModel):
    open_tickets: int = 0


class DashboardStats(BaseModel):
    users: UserStats
    services: ServiceStats
    projects: ProjectStats = ProjectStats()
    quotes: QuoteStats = QuoteStats()
    invoices: InvoiceStats = InvoiceStats()
    hosting: HostingStats = HostingStats()
    store: StoreStats = StoreStats()
    support: SupportStats = SupportStats()
