from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import ACCESS, decode_token
from app.crud import user as user_crud
from app.models.user import Role, User

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


def get_current_active_user(current_user: CurrentUser) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


ActiveUser = Annotated[User, Depends(get_current_active_user)]


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
