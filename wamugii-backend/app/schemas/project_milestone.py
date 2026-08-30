from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.project_milestone import MilestoneStatus


class ProjectMilestoneCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)
    status: MilestoneStatus = MilestoneStatus.PENDING
    display_order: int | None = Field(default=None, ge=0)
    start_date: datetime | None = None
    due_date: datetime | None = None

    @model_validator(mode="after")
    def _check_dates(self):
        if self.start_date and self.due_date and self.due_date < self.start_date:
            raise ValueError("due_date cannot be before start_date")
        return self


class ProjectMilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: MilestoneStatus | None = None
    display_order: int | None = Field(default=None, ge=0)
    start_date: datetime | None = None
    due_date: datetime | None = None

    @model_validator(mode="after")
    def _check_dates(self):
        if self.start_date and self.due_date and self.due_date < self.start_date:
            raise ValueError("due_date cannot be before start_date")
        return self


class ProjectMilestoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str
    status: MilestoneStatus
    display_order: int
    start_date: datetime | None
    due_date: datetime | None
    completed_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProjectMilestoneListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str
    status: MilestoneStatus
    display_order: int
    start_date: datetime | None
    due_date: datetime | None
    completed_at: datetime | None
    created_at: datetime


class ProjectProgressRead(BaseModel):
    project_id: int
    total_milestones: int
    completed_milestones: int
    in_progress_milestones: int
    pending_milestones: int
    progress_percentage: float
