import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.crud import hosting as hosting_crud
from app.crud import user as user_crud
from app.models.hosting import HostingStatus
from app.models.user import Role, User
from app.schemas.hosting import (
    SETTABLE_STATUSES,
    HostingAccountCreate,
    HostingAccountListItem,
    HostingAccountRead,
    HostingAccountUpdate,
    HostingPlanCreate,
    HostingPlanRead,
    HostingPlanUpdate,
)
from app.services import notifications

router = APIRouter(prefix="/hosting", tags=["hosting"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]

# Transitions the client is told about. PENDING is the creation default (already
# covered by the creation notification) and EXPIRED isn't settable, so neither
# would say anything new.
NOTIFIABLE_STATUSES = (HostingStatus.ACTIVE, HostingStatus.SUSPENDED)


def validate_client_for_hosting(db: Session, client_id: int) -> None:
    client = user_crud.get_by_id(db, client_id)
    if not client or not client.is_active or client.role != Role.CLIENT:
        raise HTTPException(
            status_code=422,
            detail="client_id must reference an active user with the CLIENT role",
        )


def validate_plan(db: Session, plan_id: int) -> None:
    plan = hosting_crud.get_plan(db, plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=422, detail="plan_id does not reference an active hosting plan"
        )


def validate_settable_status(status: HostingStatus | None) -> None:
    if status is not None and status not in SETTABLE_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=(
                "status cannot be set directly; settable values are "
                f"{sorted(s.value for s in SETTABLE_STATUSES)}"
            ),
        )


# --- plans: public read, admin write ----------------------------------------


@router.get("/plans", response_model=list[HostingPlanRead], summary="List hosting plans (public)")
def list_plans(db: DbDep, include_inactive: bool = False):
    """
    Open endpoint — the pricing page is public. `include_inactive` is honoured
    so an admin screen can reuse this, and it exposes nothing sensitive: plans
    carry only marketing copy and prices.
    """
    return hosting_crud.list_plans(db, include_inactive=include_inactive)


@router.get("/plans/{plan_id}", response_model=HostingPlanRead, summary="Get a hosting plan (public)")
def get_plan(plan_id: int, db: DbDep):
    plan = hosting_crud.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Hosting plan not found")
    return plan


@router.post(
    "/plans",
    response_model=HostingPlanRead,
    status_code=201,
    summary="Create a hosting plan (ADMIN only)",
)
def create_plan(data: HostingPlanCreate, db: DbDep, admin: AdminOnly):
    plan = hosting_crud.create_plan(db, data)
    logger.info("admin %s created hosting plan %s", admin.id, plan.id)
    return plan


@router.patch(
    "/plans/{plan_id}",
    response_model=HostingPlanRead,
    summary="Update a hosting plan (ADMIN only)",
)
def update_plan(plan_id: int, data: HostingPlanUpdate, db: DbDep, admin: AdminOnly):
    plan = hosting_crud.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Hosting plan not found")
    updated = hosting_crud.update_plan(db, plan, data)
    logger.info("admin %s updated hosting plan %s", admin.id, plan_id)
    return updated


@router.delete(
    "/plans/{plan_id}",
    response_model=HostingPlanRead,
    summary="Deactivate a hosting plan (ADMIN only, soft delete)",
)
def deactivate_plan(plan_id: int, db: DbDep, admin: AdminOnly):
    plan = hosting_crud.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Hosting plan not found")
    updated = hosting_crud.deactivate_plan(db, plan)
    logger.info("admin %s deactivated hosting plan %s", admin.id, plan_id)
    return updated


# --- accounts: staff manage -------------------------------------------------


@router.post(
    "/accounts",
    response_model=HostingAccountRead,
    status_code=201,
    summary="Create a hosting account for a client (ADMIN or STAFF)",
)
def create_account(data: HostingAccountCreate, db: DbDep, current_user: StaffOrAdmin):
    validate_client_for_hosting(db, data.client_id)
    validate_plan(db, data.plan_id)
    validate_settable_status(data.status)

    account = hosting_crud.create_account(db, data)
    logger.info(
        "staff %s created hosting account %s for client %s",
        current_user.id,
        account.id,
        data.client_id,
    )
    # Non-fatal: a notification/email problem never undoes the account.
    notifications.notify_hosting_account_created(db, account)
    return account


@router.get(
    "/accounts",
    response_model=list[HostingAccountListItem],
    summary="List hosting accounts (ADMIN or STAFF)",
)
def list_accounts(
    db: DbDep,
    current_user: StaffOrAdmin,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: HostingStatus | None = None,
    plan_id: int | None = None,
    client_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    return hosting_crud.list_accounts(
        db,
        limit=limit,
        offset=offset,
        status=status,
        plan_id=plan_id,
        client_id=client_id,
        search=search,
        include_inactive=include_inactive,
    )


@router.get(
    "/accounts/{account_id}",
    response_model=HostingAccountRead,
    summary="Get a hosting account (ADMIN or STAFF)",
)
def get_account(account_id: int, db: DbDep, current_user: StaffOrAdmin):
    account = hosting_crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Hosting account not found")
    return account


@router.patch(
    "/accounts/{account_id}",
    response_model=HostingAccountRead,
    summary="Update a hosting account (ADMIN or STAFF)",
)
def update_account(
    account_id: int, data: HostingAccountUpdate, db: DbDep, current_user: StaffOrAdmin
):
    account = hosting_crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Hosting account not found")

    validate_settable_status(data.status)
    if "plan_id" in data.model_fields_set and data.plan_id is not None:
        validate_plan(db, data.plan_id)

    # Captured before the update mutates the row in place.
    old_status = account.status
    updated = hosting_crud.update_account(db, account, data)
    logger.info(
        "staff %s updated hosting account %s: %s",
        current_user.id,
        account_id,
        data.model_dump(exclude_unset=True),
    )

    # Only a real transition into a notifiable state is an event — re-saving an
    # already-active account shouldn't email the client again.
    if updated.status != old_status and updated.status in NOTIFIABLE_STATUSES:
        notifications.notify_hosting_status_changed(db, updated)
    return updated


@router.delete(
    "/accounts/{account_id}",
    response_model=HostingAccountRead,
    summary="Deactivate a hosting account (ADMIN only, soft delete)",
)
def deactivate_account(account_id: int, db: DbDep, admin: AdminOnly):
    account = hosting_crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Hosting account not found")
    updated = hosting_crud.deactivate_account(db, account)
    logger.info("admin %s deactivated hosting account %s", admin.id, account_id)
    return updated
