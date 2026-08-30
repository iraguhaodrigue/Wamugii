from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.project import ProjectPriority, ProjectStatus


class ProjectCreate(BaseModel):
    client_id: int
    quote_request_id: int | None = None
    service_id: int | None = None
    title: str
    description: str
    priority: ProjectPriority = ProjectPriority.MEDIUM
    budget: Decimal | None = Field(default=None, ge=0)
    start_date: datetime | None = None
    deadline: datetime | None = None

    @model_validator(mode="after")
    def _check_dates(self):
        if self.start_date and self.deadline and self.deadline < self.start_date:
            raise ValueError("deadline cannot be before start_date")
        return self


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    priority: ProjectPriority | None = None
    budget: Decimal | None = Field(default=None, ge=0)
    amount_paid: Decimal | None = Field(default=None, ge=0)
    start_date: datetime | None = None
    deadline: datetime | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    quote_request_id: int | None
    service_id: int | None
    title: str
    description: str
    status: ProjectStatus
    priority: ProjectPriority
    budget: Decimal | None
    amount_paid: Decimal
    start_date: datetime | None
    deadline: datetime | None
    completed_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProjectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    service_id: int | None
    title: str
    status: ProjectStatus
    priority: ProjectPriority
    budget: Decimal | None
    amount_paid: Decimal
    deadline: datetime | None
    is_active: bool
    created_at: datetime
