import logging

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import ActiveUser, DbDep
from app.crud import notification as notification_crud
from app.schemas.notification import MarkAllReadResponse, NotificationRead, UnreadCountRead

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

# Every route below is scoped to `current_user.id`. There is no role gate and no
# `user_id` parameter anywhere: a user can only ever reach their own rows, and
# anything belonging to someone else 404s rather than 403s (same convention as
# projects/invoices — a 403 would confirm the row exists).


@router.get("", response_model=list[NotificationRead], summary="List your own notifications")
def list_notifications(
    db: DbDep,
    current_user: ActiveUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = False,
):
    return notification_crud.list_for_user(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountRead,
    summary="Count your unread notifications (for the bell badge)",
)
def unread_count(db: DbDep, current_user: ActiveUser):
    return UnreadCountRead(unread=notification_crud.count_unread(db, current_user.id))


@router.patch(
    "/read-all",
    response_model=MarkAllReadResponse,
    summary="Mark all of your notifications read",
)
def mark_all_read(db: DbDep, current_user: ActiveUser):
    # Declared before /{notification_id}/read so the literal path wins the match.
    updated = notification_crud.mark_all_read(db, current_user.id)
    return MarkAllReadResponse(updated=updated)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationRead,
    summary="Mark one of your notifications read",
)
def mark_read(notification_id: int, db: DbDep, current_user: ActiveUser):
    notification = notification_crud.get_for_user(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification_crud.mark_read(db, notification)
