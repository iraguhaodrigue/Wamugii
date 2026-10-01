from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project_member import ProjectRole


class ProjectMemberCreate(BaseModel):
    user_id: int
    project_role: ProjectRole = ProjectRole.PROGRAMMER


class ProjectMemberUpdate(BaseModel):
    project_role: ProjectRole


class ProjectMemberRead(BaseModel):
    """
    The ADMIN/STAFF view of a membership.

    The member's name and email are included because staff manage assignments
    and need to know who they are picking. This schema is never returned to a
    TEAM_MEMBER -- their own view is in schemas/team.py.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    user_id: int
    project_role: ProjectRole
    assigned_at: datetime
    assigned_by: int
    is_active: bool

    # Resolved by the router from the joined user row.
    user_full_name: str | None = None
    user_email: str | None = None
    user_role: str | None = None
