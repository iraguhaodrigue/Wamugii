import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbDep, require_roles
from app.crud import company_settings as settings_crud
from app.models.user import Role, User
from app.schemas.company_settings import (
    CompanySettingsPublicRead,
    CompanySettingsRead,
    CompanySettingsUpdate,
)

router = APIRouter(prefix="/settings", tags=["settings"])
logger = logging.getLogger(__name__)

AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]


@router.get(
    "/public",
    response_model=CompanySettingsPublicRead,
    summary="Public company info (no auth) — excludes TIN and notification routing",
)
def get_public_settings(db: DbDep):
    """
    Open endpoint for the marketing site's contact details. The response model
    has no `tin` or `notification_email` field at all, so neither can escape
    here even though the underlying row carries them.
    """
    return settings_crud.get_settings(db)


@router.get("", response_model=CompanySettingsRead, summary="Get company settings (ADMIN only)")
def get_settings(db: DbDep, admin: AdminOnly):
    return settings_crud.get_settings(db)


@router.patch("", response_model=CompanySettingsRead, summary="Update company settings (ADMIN only)")
def update_settings(data: CompanySettingsUpdate, db: DbDep, admin: AdminOnly):
    updated = settings_crud.update_settings(db, data)
    logger.info(
        "admin %s updated company settings: %s",
        admin.id,
        # Values can include the TIN and an internal address — log which fields
        # changed, never what they changed to.
        sorted(data.model_dump(exclude_unset=True)),
    )
    return updated
