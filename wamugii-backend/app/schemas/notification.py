from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationType


class NotificationRead(BaseModel):
    """
    A notification as its own recipient sees it. There is no Create schema on
    purpose — notifications are emitted by the system, never posted by a client.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    read_at: datetime | None
    related_type: str | None
    related_id: int | None
    created_at: datetime


class UnreadCountRead(BaseModel):
    """Payload for the bell badge."""

    unread: int


class MarkAllReadResponse(BaseModel):
    """How many of the caller's notifications this request flipped to read."""

    updated: int
