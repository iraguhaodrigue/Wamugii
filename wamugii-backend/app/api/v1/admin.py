import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DbDep, require_roles
from app.crud import invoice as invoice_crud
from app.crud import project as project_crud
from app.crud import quote_request as quote_crud
from app.crud import service as service_crud
from app.crud import user as user_crud
from app.models.user import Role, User
from app.schemas.admin import (
    DashboardStats,
    InvoiceStats,
    ProjectStats,
    QuoteStats,
    ServiceStats,
    UserStats,
)
from app.schemas.user import UserAdminUpdate, UserRead

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

CurrentAdmin = Annotated[User, Depends(require_roles(Role.ADMIN))]


def _assert_not_last_admin(db: DbDep, user: User, *, will_lose_admin_access: bool) -> None:
    if user.role == Role.ADMIN and user.is_active and will_lose_admin_access:
        if user_crud.count_active_admins(db) <= 1:
            raise HTTPException(
                status_code=409,
                detail="Cannot remove, deactivate, or demote the last active admin",
            )


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: DbDep, admin: CurrentAdmin):
    return DashboardStats(
        users=UserStats(
            total=user_crud.count_all(db),
            clients=user_crud.count_by_role(db, Role.CLIENT),
            staff=user_crud.count_by_role(db, Role.STAFF),
            admins=user_crud.count_by_role(db, Role.ADMIN),
        ),
        services=ServiceStats(
            total=service_crud.count_total(db),
            active=service_crud.count_active(db),
        ),
        quotes=QuoteStats(pending=quote_crud.count_pending(db)),
        projects=ProjectStats(
            total=project_crud.count_total(db),
            active=project_crud.count_active(db),
        ),
        invoices=InvoiceStats(
            pending=invoice_crud.count_outstanding(db),
            outstanding=invoice_crud.sum_outstanding(db),
        ),
        # TODO: hosting module not built yet
        # TODO: store module not built yet
        # TODO: support module not built yet
    )


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: DbDep,
    admin: CurrentAdmin,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = None,
    role: Role | None = None,
):
    return user_crud.list_admin(db, limit=limit, offset=offset, search=search, role=role)


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: DbDep, admin: CurrentAdmin):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserAdminUpdate, db: DbDep, admin: CurrentAdmin):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    will_lose_admin_access = (data.role is not None and data.role != Role.ADMIN) or (
        data.is_active is False
    )
    _assert_not_last_admin(db, user, will_lose_admin_access=will_lose_admin_access)

    updated = user_crud.update_admin_fields(db, user, data)
    logger.info(
        "admin %s updated user %s: %s", admin.id, user_id, data.model_dump(exclude_unset=True)
    )
    return updated


@router.delete("/users/{user_id}", response_model=UserRead)
def deactivate_user(user_id: int, db: DbDep, admin: CurrentAdmin):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    _assert_not_last_admin(db, user, will_lose_admin_access=True)

    updated = user_crud.deactivate(db, user)
    logger.info("admin %s deactivated user %s", admin.id, user_id)
    return updated
