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
    pending: int = 0


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
