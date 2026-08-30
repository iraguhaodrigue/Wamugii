from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import ActiveUser, DbDep
from app.core.security import REFRESH, create_access_token, create_refresh_token, decode_token
from app.crud import user as user_crud
from app.schemas.token import RefreshRequest, Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


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
def me(current_user: ActiveUser):
    return current_user


@router.post("/logout")
def logout():
    # JWT is stateless: the client just deletes its tokens.
    # For true server-side revocation later, add a token blocklist in Redis.
    return {"detail": "Logged out. Delete your tokens on the client."}
