from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.deps import ActiveUser, DbDep, require_roles
from app.crud import user as user_crud
from app.models.user import Role, User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: ActiveUser):
    return current_user


@router.get(
    "",
    response_model=list[UserRead],
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def list_users(db: DbDep):
    return db.scalars(select(User).order_by(User.id)).all()


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def get_user(user_id: int, db: DbDep):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
