from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.models.domain import DomainStatus

Availability = Literal["available", "taken", "unknown"]


class DomainCheckResult(BaseModel):
    domain: str
    extension: str
    status: Availability
    price: Decimal | None = Field(
        default=None, description="Price per year in RWF; null when we do not sell this extension online"
    )
    expires_at: date | None = None
    registrar: str | None = None
    reason: str | None = None


class DomainSearchResponse(BaseModel):
    query: str
    name: str
    results: list[DomainCheckResult]
    suggestions: list[DomainCheckResult]
    checked_at: datetime
    note: str = (
        "Availability comes straight from each registry. A few names are reserved or premium; "
        "we confirm the final availability when we register it for you."
    )


class DomainOrderCreate(BaseModel):
    domain_name: str = Field(min_length=3, max_length=255)
    years: int = Field(default=1, ge=1, le=5)


# --- dashboard ---------------------------------------------------------------


class DashboardDomainRow(BaseModel):
    id: int
    domain_name: str
    client_id: int
    client_name: str
    status: DomainStatus
    total_fee: Decimal
    created_at: datetime
    expires_at: date | None = None
    days_left: int | None = None
    auto_renew: bool = False


class ExtensionCount(BaseModel):
    extension: str
    count: int


class SearchedName(BaseModel):
    name: str
    searches: int
    last_searched: datetime


class DomainDashboard(BaseModel):
    counts: dict[str, int]
    yearly_value: Decimal
    pending_requests: list[DashboardDomainRow]
    expiring: list[DashboardDomainRow]
    by_extension: list[ExtensionCount]
    searches_7_days: int
    searches_30_days: int
    top_searches: list[SearchedName]
    available_share: float | None
