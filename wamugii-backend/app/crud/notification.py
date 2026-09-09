from datetime import datetime, timezone

from sqlalchemy import func, select, update as sql_update
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType


def create(
    db: Session,
    *,
    user_id: int,
    type: NotificationType,
    title: str,
    message: str,
    related_type: str | None = None,
    related_id: int | None = None,
) -> Notification:
    """
    Low-level insert. Callers should go through services/notifications.py, which
    wraps this so a notification failure can never break the action that
    triggered it.
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        related_type=related_type,
        related_id=related_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_for_user(db: Session, notification_id: int, user_id: int) -> Notification | None:
    """
    Scoped fetch — a notification belonging to anyone else comes back as None,
    which the router turns into a 404 (never 403).
    """
    return db.scalar(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
    )


def list_for_user(
    db: Session,
    user_id: int,
    *,
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    query = query.order_by(Notification.created_at.desc(), Notification.id.desc())
    query = query.offset(offset).limit(limit)
    return list(db.scalars(query).all())


def count_unread(db: Session, user_id: int) -> int:
    """SQL COUNT for the bell badge — never loads rows."""
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        or 0
    )


def mark_read(db: Session, notification: Notification) -> Notification:
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_read(db: Session, user_id: int) -> int:
    """
    Bulk UPDATE scoped to this user — one statement rather than loading and
    saving each row. Returns how many were flipped.
    """
    result = db.execute(
        sql_update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    db.commit()
    return result.rowcount or 0
