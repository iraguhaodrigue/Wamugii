from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    short_description: str | None = None
    description: str | None = None
    category: str | None = None
    icon: str | None = None
    image: str | None = None
    price_from: Decimal | None = None
    is_active: bool = True
    display_order: int = 0


class ServiceCreate(ServiceBase):
    slug: str | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    short_description: str | None = None
    description: str | None = None
    category: str | None = None
    icon: str | None = None
    image: str | None = None
    price_from: Decimal | None = None
    is_active: bool | None = None
    display_order: int | None = None


class ServiceRead(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
