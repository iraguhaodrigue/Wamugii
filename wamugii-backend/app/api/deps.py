from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import ACCESS, decode_token
from app.crud import user as user_crud
from app.models.user import ApprovalStatus, Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbDep, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != ACCESS:
            raise cred_exc
        user_id = payload.get("sub")
        if user_id is None:
            raise cred_exc
    except jwt.PyJWTError:
        raise cred_exc

    user = user_crud.get_by_id(db, int(user_id))
    if user is None:
        raise cred_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

# One wording for each blocked approval state, so the frontend can match on it
# and so an unapproved user is never left guessing.
PENDING_APPROVAL_MESSAGE = (
    "Your account is pending approval. An administrator will review your "
    "registration and you'll be emailed once it's approved."
)
REJECTED_ACCOUNT_MESSAGE = (
    "Your account registration was not approved. Please contact WAMUGII if you "
    "think this is a mistake."
)
# A TEAM_MEMBER is a project collaborator, not an account manager. Everything
# outside /team (and their own notifications) is closed to them.
TEAM_MEMBER_FORBIDDEN_MESSAGE = (
    "Team members don't have access to this area. Your projects are under /team."
)


def get_current_user_any_approval(current_user: CurrentUser) -> User:
    """
    Active user, approved or not.

    Exists for exactly one reason: the "you're awaiting approval" screen needs
    /auth/me to work, so the two `me` endpoints read the account through this
    instead of `ActiveUser`. Nothing else should use it -- a PENDING account has
    no business reaching any other endpoint.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


AnyApprovalUser = Annotated[User, Depends(get_current_user_any_approval)]


def get_current_active_user(current_user: CurrentUser) -> User:
    """
    The gate every protected endpoint passes through, directly or via
    `require_roles` (which depends on this). Putting the approval check here
    means a PENDING account is locked out of the whole API by construction,
    rather than endpoint by endpoint.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.approval_status == ApprovalStatus.PENDING:
        raise HTTPException(status_code=403, detail=PENDING_APPROVAL_MESSAGE)
    if current_user.approval_status == ApprovalStatus.REJECTED:
        raise HTTPException(status_code=403, detail=REJECTED_ACCOUNT_MESSAGE)
    return current_user


ActiveUser = Annotated[User, Depends(get_current_active_user)]


def forbid_team_member(current_user: ActiveUser) -> User:
    """
    `ActiveUser` for endpoints that are role-scoped rather than role-gated.

    `/projects`, its milestones and its files all accept any authenticated user
    and then narrow by role, which would have handed a TEAM_MEMBER the full
    `ProjectRead` -- client_id, budget, amount_paid and all -- for every project
    in the system. They read through this instead. Endpoints that already go
    through `require_roles` need nothing: TEAM_MEMBER is in none of their role
    lists, so they 403 on their own.
    """
    if current_user.role == Role.TEAM_MEMBER:
        raise HTTPException(status_code=403, detail=TEAM_MEMBER_FORBIDDEN_MESSAGE)
    return current_user


NonTeamUser = Annotated[User, Depends(forbid_team_member)]


oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False
)


def get_current_user_optional(db: DbDep, token: Annotated[str | None, Depends(oauth2_scheme_optional)]) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != ACCESS:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None
    return user_crud.get_by_id(db, int(user_id))


OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]


def require_roles(*roles: Role):
    def checker(current_user: ActiveUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return checker
