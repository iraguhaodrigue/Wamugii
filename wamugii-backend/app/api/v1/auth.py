import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AnyApprovalUser, DbDep
from app.core.config import settings
from app.core.security import REFRESH, create_access_token, create_refresh_token, decode_token
from app.crud import password_reset_token as reset_crud
from app.crud import user as user_crud
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from app.schemas.token import RefreshRequest, Token
from app.models.user import ApprovalStatus, Role
from app.schemas.user import TeamMemberRegister, UserCreate, UserRead
from app.services import email_service, email_templates, notifications

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# One response for every forgot-password outcome, so the endpoint can't be used
# to discover which addresses have accounts.
FORGOT_PASSWORD_RESPONSE = (
    "If an account exists for that email, a password reset link has been sent."
)

# One response for every invalid token, so an attacker can't tell an expired
# token from a spent one from a fabricated one.
INVALID_TOKEN_MESSAGE = (
    "This reset link has expired or has already been used. Please request a new one."
)


def _token_pair(user_id: int) -> Token:
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: DbDep):
    if user_crud.get_by_email(db, data.email.lower()):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create(db, data)


TEAM_MEMBER_PENDING_RESPONSE = (
    "Thanks for registering. Your account is pending admin approval — we'll email "
    "you as soon as it's approved."
)


@router.post("/register-team-member", response_model=MessageResponse, status_code=201)
def register_team_member(data: TeamMemberRegister, db: DbDep):
    """
    Public self-registration for a project collaborator.

    The account is created PENDING: it can log in, but the approval gate in
    `deps.get_current_active_user` closes every other endpoint until an admin
    approves it.

    Returns a message rather than the user row, and the *same* message whether
    or not the address was already taken — otherwise this endpoint becomes an
    account-enumeration oracle, the same reasoning as forgot-password. A
    duplicate simply creates nothing.
    """
    existing = user_crud.get_by_email(db, data.email.lower())
    if existing is not None:
        logger.info("team member registration for an address that already has an account")
        return MessageResponse(detail=TEAM_MEMBER_PENDING_RESPONSE)

    user = user_crud.create(
        db,
        UserCreate(
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            password=data.password,
        ),
        role=Role.TEAM_MEMBER,
        approval_status=ApprovalStatus.PENDING,
    )
    logger.info("team member %s self-registered, pending approval", user.id)
    notifications.notify_team_member_registered(db, user)
    return MessageResponse(detail=TEAM_MEMBER_PENDING_RESPONSE)


@router.post("/login", response_model=Token)
def login(db: DbDep, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # NOTE: put the email in the "username" field.
    user = user_crud.authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return _token_pair(user.id)


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: DbDep):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != REFRESH:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = int(payload.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = user_crud.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return _token_pair(user.id)


@router.get("/me", response_model=UserRead)
def me(current_user: AnyApprovalUser):
    """
    Readable by a PENDING account on purpose: it is how the frontend learns to
    show the awaiting-approval screen rather than a dashboard. The response
    carries no data the caller didn't already supply about themselves.
    """
    return current_user


def _reset_url(token: str) -> str | None:
    """The frontend link for a token, or None when FRONTEND_URL isn't set."""
    base = settings.FRONTEND_URL
    if not base:
        return None
    return f"{base.rstrip('/')}/reset-password?token={token}"


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest, db: DbDep):
    """
    Start a password reset.

    Always answers with the same body, whether or not the address has an
    account and whether or not the email actually went out — otherwise the
    response becomes an account-enumeration oracle.
    """
    user = user_crud.get_by_email(db, data.email.lower())

    if user is not None and user.is_active:
        # Reuse a live token instead of minting one per submission, so repeated
        # clicks on the form don't send a burst of emails.
        existing = reset_crud.get_usable_for_user(db, user.id)
        row = existing or reset_crud.create_for_user(db, user.id)

        if existing is None:
            # Only mail on a freshly issued token; re-sending the same link on
            # every submit would defeat the point of reusing it.
            try:
                subject, html, text = email_templates.password_reset(user, _reset_url(row.token))
                email_service.send_email(
                    to_email=user.email,
                    to_name=user.full_name,
                    subject=subject,
                    html_content=html,
                    text_content=text,
                )
            except Exception:
                # Non-fatal, like every other send in the app: the token exists,
                # the caller still gets the neutral response.
                logger.exception("failed to send the password reset email for user %s", user.id)
        logger.info("password reset requested for user %s", user.id)
    else:
        # Logged without the address so the log isn't itself an enumeration aid.
        logger.info("password reset requested for an unknown or inactive account")

    return MessageResponse(detail=FORGOT_PASSWORD_RESPONSE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: DbDep):
    """
    Complete a password reset.

    Every failure — unknown token, expired, already spent, deactivated user —
    returns the same 400 so none of them can be told apart.
    """
    row = reset_crud.get_by_token(db, data.token)
    if row is None or not reset_crud.is_usable(row):
        raise HTTPException(status_code=400, detail=INVALID_TOKEN_MESSAGE)

    user = user_crud.get_by_id(db, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail=INVALID_TOKEN_MESSAGE)

    user_crud.set_password(db, user, data.password)
    # Spends the clicked token *and* any other outstanding one for this user,
    # so a second link that was issued earlier can't be replayed.
    reset_crud.invalidate_all_for_user(db, user.id)
    logger.info("password reset completed for user %s", user.id)

    return MessageResponse(detail="Your password has been reset. You can now log in.")


@router.post("/logout")
def logout():
    # JWT is stateless: the client just deletes its tokens.
    # For true server-side revocation later, add a token blocklist in Redis.
    return {"detail": "Logged out. Delete your tokens on the client."}
