import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DbDep, require_roles
from app.crud import hosting as hosting_crud
from app.crud import invoice as invoice_crud
from app.crud import project as project_crud
from app.crud import quote_request as quote_crud
from app.crud import service as service_crud
from app.crud import support as support_crud
from app.crud import user as user_crud
from app.models.user import ApprovalStatus, Role, User
from app.schemas.admin import (
    DashboardStats,
    HostingStats,
    InvoiceStats,
    ProjectStats,
    QuoteStats,
    ServiceStats,
    SupportStats,
    TeamStats,
    UserStats,
)
from app.schemas.user import RejectTeamMemberRequest, UserAdminUpdate, UserRead
from app.services import notifications

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
        hosting=HostingStats(active=hosting_crud.count_active_accounts(db)),
        # TODO: store module not built yet
        support=SupportStats(open_tickets=support_crud.count_open_tickets(db)),
        team=TeamStats(
            pending_approvals=user_crud.count_team_members(
                db, approval_status=ApprovalStatus.PENDING
            ),
            approved_members=user_crud.count_team_members(
                db, approval_status=ApprovalStatus.APPROVED
            ),
        ),
    )


# --- team member approval ---------------------------------------------------
#
# Registration itself is public (auth/register-team-member). These three are
# the admin side of it: see who is waiting, let them in, or turn them down.


def _get_team_member(db: DbDep, user_id: int) -> User:
    """
    A team member by id, 404 for anything else.

    Guards the obvious foot-gun: these endpoints must not be usable to flip the
    approval flag on a CLIENT, STAFF or ADMIN account.
    """
    user = user_crud.get_by_id(db, user_id)
    if not user or user.role != Role.TEAM_MEMBER:
        raise HTTPException(status_code=404, detail="Team member not found")
    return user


@router.get(
    "/team-members/pending",
    response_model=list[UserRead],
    summary="List team member registrations awaiting approval (ADMIN only)",
)
def list_pending_team_members(
    db: DbDep,
    admin: CurrentAdmin,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return user_crud.list_team_members(
        db, approval_status=ApprovalStatus.PENDING, limit=limit, offset=offset
    )


@router.get(
    "/team-members",
    response_model=list[UserRead],
    summary="List team members, optionally by approval status (ADMIN only)",
)
def list_team_members(
    db: DbDep,
    admin: CurrentAdmin,
    approval_status: ApprovalStatus | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return user_crud.list_team_members(
        db, approval_status=approval_status, limit=limit, offset=offset
    )


@router.patch(
    "/team-members/{user_id}/approve",
    response_model=UserRead,
    summary="Approve a team member registration (ADMIN only)",
)
def approve_team_member(user_id: int, db: DbDep, admin: CurrentAdmin):
    user = _get_team_member(db, user_id)
    if user.approval_status == ApprovalStatus.APPROVED:
        # Idempotent, but don't re-notify someone who was already approved.
        return user

    updated = user_crud.set_approval_status(db, user, ApprovalStatus.APPROVED)
    logger.info("admin %s approved team member %s", admin.id, user_id)
    notifications.notify_team_member_approved(db, updated)
    return updated


@router.patch(
    "/team-members/{user_id}/reject",
    response_model=UserRead,
    summary="Reject a team member registration (ADMIN only)",
)
def reject_team_member(
    user_id: int,
    db: DbDep,
    admin: CurrentAdmin,
    data: RejectTeamMemberRequest | None = None,
):
    user = _get_team_member(db, user_id)
    if user.approval_status == ApprovalStatus.REJECTED:
        return user

    updated = user_crud.set_approval_status(db, user, ApprovalStatus.REJECTED)
    logger.info("admin %s rejected team member %s", admin.id, user_id)
    notifications.notify_team_member_rejected(db, updated, data.reason if data else None)
    return updated


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
