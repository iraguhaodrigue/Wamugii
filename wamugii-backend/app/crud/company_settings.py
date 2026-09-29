from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.company_settings import SETTINGS_ID, CompanySettings
from app.schemas.company_settings import CompanySettingsUpdate


def get_settings(db: Session) -> CompanySettings:
    """
    The settings row, created with defaults on first read.

    Upsert-on-read rather than a seed script: the row must exist the first time
    anything asks for it (an invoice render, a quote email), and there is no
    install step that would guarantee that otherwise. The IntegrityError retry
    covers two requests racing to create it — the primary key is the guard.
    """
    existing = db.get(CompanySettings, SETTINGS_ID)
    if existing is not None:
        return existing

    settings_row = CompanySettings(id=SETTINGS_ID)
    db.add(settings_row)
    try:
        db.commit()
    except IntegrityError:
        # Someone else created it between the get and the insert.
        db.rollback()
        raced = db.get(CompanySettings, SETTINGS_ID)
        if raced is not None:
            return raced
        raise
    db.refresh(settings_row)
    return settings_row


def update_settings(db: Session, data: CompanySettingsUpdate) -> CompanySettings:
    """Partial update — only fields present in the request are touched."""
    settings_row = get_settings(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings_row, field, value)
    db.commit()
    db.refresh(settings_row)
    return settings_row
