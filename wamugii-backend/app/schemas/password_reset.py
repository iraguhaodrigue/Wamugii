from pydantic import BaseModel, EmailStr, Field

# Same minimum as registration — imported rather than redeclared so the two
# can't drift.
from app.schemas.user import MIN_PASSWORD_LENGTH


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class MessageResponse(BaseModel):
    """
    Plain acknowledgement, matching the shape /auth/logout already returns.

    Forgot-password deliberately answers with the same body whether or not the
    address belongs to an account, so this response reveals nothing.
    """

    detail: str
