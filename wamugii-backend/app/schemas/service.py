from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.json_list import parse_json_list


class ServiceBase(BaseModel):
    name: str
    short_description: str | None = None
    description: str | None = None
    # The "explore" detail. Both optional and both additive -- a service with
    # neither renders exactly as it did before these existed.
    long_description: str | None = None
    features: list[str] | None = None
    category: str | None = None
    icon: str | None = None
    image: str | None = None
    price_from: Decimal | None = None
    is_active: bool = True
    display_order: int = 0


    _parse_features = field_validator("features", mode="before")(parse_json_list)


class ServiceCreate(ServiceBase):
    slug: str | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    short_description: str | None = None
    description: str | None = None
    long_description: str | None = None
    features: list[str] | None = None
    category: str | None = None
    icon: str | None = None
    image: str | None = None
    price_from: Decimal | None = None
    is_active: bool | None = None
    display_order: int | None = None

    _parse_features = field_validator("features", mode="before")(parse_json_list)


class ServiceRead(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
