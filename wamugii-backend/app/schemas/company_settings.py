from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanySettingsRead(BaseModel):
    """Full settings, ADMIN only — includes the TIN and notification routing."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    slogan: str
    tin: str | None
    address: str | None
    phone: str | None
    email: str | None
    website: str | None
    notification_email: str | None
    updated_at: datetime


class CompanySettingsPublicRead(BaseModel):
    """
    The safe subset, served unauthenticated.

    `tin` and `notification_email` are deliberately absent from this model, not
    merely blanked: the TIN belongs on an invoice rather than an open endpoint,
    and the notification address is internal routing. Because the fields are
    not declared here, they cannot leak even if someone later returns the whole
    ORM row through this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    company_name: str
    slogan: str
    address: str | None
    phone: str | None
    email: str | None
    website: str | None


class CompanySettingsUpdate(BaseModel):
    """Every field optional — this is a partial update."""

    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    slogan: str | None = Field(default=None, max_length=255)
    tin: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=255)
    notification_email: EmailStr | None = None


class InvoiceCompanyBlock(BaseModel):
    """
    The issuer details printed at the top of an invoice.

    Read from settings at render time rather than copied onto each invoice row:
    correcting a typo in the address should fix every invoice, and the TIN is a
    property of the company, not of one bill.
    """

    model_config = ConfigDict(from_attributes=True)

    company_name: str
    tin: str | None
    address: str | None
    phone: str | None
    email: str | None
