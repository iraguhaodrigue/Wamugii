from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.quote_request import QuoteStatus


class QuoteRequestCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    company_name: str | None = None
    service_id: int | None = None
    project_title: str
    project_description: str
    budget_range: str | None = None
    preferred_deadline: str | None = None


class QuoteRequestPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str
    company_name: str | None
    service_id: int | None
    project_title: str
    project_description: str
    budget_range: str | None
    preferred_deadline: str | None
    status: QuoteStatus
    created_at: datetime


class QuoteRequestRead(QuoteRequestPublicRead):
    admin_notes: str | None
    is_active: bool
    updated_at: datetime


class QuoteRequestAdminUpdate(BaseModel):
    status: QuoteStatus | None = None
    admin_notes: str | None = None
