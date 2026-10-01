from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import ApprovalStatus, Role

# The one place the password rule lives. The reset schema imports this so
# registration and password reset can never drift apart, and the Register /
# Reset forms enforce the same number client-side.
MIN_PASSWORD_LENGTH = 8


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Role
    # The frontend needs this to show the "awaiting approval" screen instead of
    # a dashboard, so it travels on /auth/me like `role` does.
    approval_status: ApprovalStatus
    is_active: bool
    created_at: datetime


class TeamMemberRegister(BaseModel):
    """
    Public self-registration for a project collaborator.

    Separate from `UserCreate` on purpose: `role` and `approval_status` are set
    by the endpoint, never by the caller, so there is no field here that could
    be used to self-approve or to claim a different role.
    """

    full_name: str
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class RejectTeamMemberRequest(BaseModel):
    """Optional note for the rejection email. Nothing is required."""

    reason: str | None = Field(default=None, max_length=1000)


class UserAdminUpdate(BaseModel):
    role: Role | None = None
    is_active: bool | None = None
