from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.domain_extension import DEFAULT_MARGIN


def _normalise_extension(value: str) -> str:
    """
    One normalised form across the schema and the UI.

    An admin can type ".com", "com" or ".COM" and the stored form is the same.
    Keeps the uniqueness constraint from fragmenting on spelling.
    """
    text = (value or "").strip().lower()
    if not text:
        raise ValueError("extension cannot be empty")
    if not text.startswith("."):
        text = "." + text
    # Rough-and-ready: letters, digits and the leading dot. Prevents whole URLs
    # from being pasted into this field by accident.
    body = text[1:]
    if not body or any(c in body for c in " /\\?#:@") or "." in body:
        raise ValueError("extension must be a single TLD like '.com' or '.rw'")
    return text


class DomainExtensionBase(BaseModel):
    extension: str = Field(min_length=2, max_length=16)
    cost_price: Decimal = Field(ge=0)
    margin: Decimal = Field(default=DEFAULT_MARGIN, ge=0)
    is_active: bool = True
    display_order: int = 0

    @field_validator("extension")
    @classmethod
    def _extension_normalised(cls, value: str) -> str:
        return _normalise_extension(value)


class DomainExtensionCreate(DomainExtensionBase):
    pass


class DomainExtensionUpdate(BaseModel):
    """Every field optional; the extension string itself is immutable."""

    cost_price: Decimal | None = Field(default=None, ge=0)
    margin: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None
    display_order: int | None = None


class DomainExtensionRead(BaseModel):
    """
    Public read shape.

    `client_price` is computed server-side on every read -- changing cost or
    margin updates it everywhere without touching the row, which is the whole
    point of not storing it.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    extension: str
    cost_price: Decimal
    margin: Decimal
    client_price: Decimal
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
