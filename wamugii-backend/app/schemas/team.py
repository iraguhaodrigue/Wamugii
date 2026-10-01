"""
The team-member read surface -- the privacy wall, expressed as types.

A TEAM_MEMBER is a collaborator, not an account manager: they must never learn
who the client is, what the project is worth, or anything about billing. These
schemas are the enforcement, not a convenience:

* Pydantic serializes **only declared fields**, so `TeamProjectDetail` built
  from a `Project` row physically cannot emit `client_id`, `budget`,
  `amount_paid` or `quote_request_id` -- the fields are not on the model, so
  there is nothing to leak even if a future change adds columns to `Project`.
* `TeamProjectFile` deliberately omits `uploaded_by`. A client can upload files
  to their own project, so that column can hold a client's user id, which is
  client-identifying information by the back door.
* `service_id` is omitted too. It is harmless on its own, but the services
  endpoint is public, so it is simply not needed for the technical work.

`test_team_members.py` asserts the absence of every one of those keys in the
raw response body, and also that the client's name string appears nowhere in
it, so this comment cannot quietly drift away from the behaviour.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectPriority, ProjectStatus
from app.models.project_file import FileCategory
from app.models.project_member import ProjectRole
from app.models.project_milestone import MilestoneStatus


class TeamProjectMilestone(BaseModel):
    """Technical milestone view -- no money, no client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: MilestoneStatus
    display_order: int
    start_date: datetime | None
    due_date: datetime | None
    completed_at: datetime | None


class TeamProjectFile(BaseModel):
    """File metadata minus `uploaded_by` -- see the module docstring."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    content_type: str
    file_size: int
    category: FileCategory
    description: str | None
    created_at: datetime


class TeamProjectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: ProjectStatus
    priority: ProjectPriority
    deadline: datetime | None
    created_at: datetime

    # The member's own role on this project, resolved from their membership.
    my_role: ProjectRole


class TeamProjectDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: ProjectStatus
    priority: ProjectPriority
    start_date: datetime | None
    deadline: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    my_role: ProjectRole
    milestones: list[TeamProjectMilestone] = []
    files: list[TeamProjectFile] = []
