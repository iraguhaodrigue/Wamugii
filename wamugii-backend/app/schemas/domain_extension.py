import re
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
    # Letters, digits and hyphens, in one or two dot-separated parts, so
    # second-level extensions such as ".co.rw" and ".ac.rw" are allowed while
    # whole URLs pasted by accident are still rejected.
    body = text[1:]
    labels = body.split(".")
    if (
        not body
        or len(labels) > 2
        or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) for label in labels)
    ):
        raise ValueError("extension must look like '.com', '.rw' or '.co.rw'")
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


class DomainExtensionPublic(BaseModel):
    """
    What visitors see: the extension and its yearly price only. The cost price
    and margin are business information and stay on the admin endpoints.
    """

    model_config = ConfigDict(from_attributes=True)

    extension: str
    client_price: Decimal
    display_order: int
