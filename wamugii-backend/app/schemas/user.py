from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Role

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
    is_active: bool
    created_at: datetime


class UserAdminUpdate(BaseModel):
    role: Role | None = None
    is_active: bool | None = None
