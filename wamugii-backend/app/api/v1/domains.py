import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.crud import domain as domain_crud
from app.crud import domain_extension as extension_crud
from app.crud import hosting as hosting_crud
from app.crud import user as user_crud
from app.models.domain import DomainStatus
from app.models.user import Role, User
from app.schemas.domain import (
    SETTABLE_STATUSES,
    DomainCreate,
    DomainListItem,
    DomainRead,
    DomainUpdate,
)
from app.schemas.domain_extension import (
    DomainExtensionCreate,
    DomainExtensionRead,
    DomainExtensionUpdate,
)
from app.services import notifications

router = APIRouter(prefix="/domains", tags=["domains"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]

# Transitions the client hears about. PENDING is the creation default (already
# covered by the registration email), so it would say nothing new.
NOTIFIABLE_STATUSES = (DomainStatus.ACTIVE, DomainStatus.EXPIRED, DomainStatus.CANCELLED)


def validate_client_for_domain(db: Session, client_id: int) -> None:
    client = user_crud.get_by_id(db, client_id)
    if not client or not client.is_active or client.role != Role.CLIENT:
        raise HTTPException(
            status_code=422,
            detail="client_id must reference an active user with the CLIENT role",
        )


def validate_hosting_account(db: Session, hosting_account_id: int, client_id: int) -> None:
    """
    A linked hosting account must exist, be active, and belong to the same
    client — the rule invoices and tickets already enforce.
    """
    account = hosting_crud.get_account(db, hosting_account_id)
    if not account or not account.is_active:
        raise HTTPException(
            status_code=422,
            detail="hosting_account_id does not reference an active hosting account",
        )
    if account.client_id != client_id:
        raise HTTPException(
            status_code=422,
            detail="hosting_account_id belongs to a different client",
        )


def validate_settable_status(status: DomainStatus | None) -> None:
    if status is not None and status not in SETTABLE_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=(
                "status cannot be set directly; settable values are "
                f"{sorted(s.value for s in SETTABLE_STATUSES)}"
            ),
        )


@router.post(
    "",
    response_model=DomainRead,
    status_code=201,
    summary="Register a domain for a client (ADMIN or STAFF)",
)
def create_domain(data: DomainCreate, db: DbDep, current_user: StaffOrAdmin):
    validate_client_for_domain(db, data.client_id)
    if data.hosting_account_id is not None:
        validate_hosting_account(db, data.hosting_account_id, data.client_id)
    validate_settable_status(data.status)

    # Prefill fees from the price list when the admin didn't send them.
    # "Didn't send" means the field wasn't in the payload at all; an explicit
    # 0 is left alone, so a legitimate free registration is never overwritten.
    # Only the matched extension's row is consulted; an unknown TLD still
    # creates fine, just without prefill.
    sent = data.model_fields_set
    if "registration_fee" not in sent or "service_fee" not in sent:
        matched = extension_crud.match_for_domain_name(db, data.domain_name)
        if matched is not None and matched.is_active:
            if "registration_fee" not in sent:
                data.registration_fee = matched.cost_price
            if "service_fee" not in sent:
                data.service_fee = matched.margin

    domain = domain_crud.create_domain(db, data)
    logger.info(
        "staff %s registered domain %s (%s) for client %s",
        current_user.id,
        domain.id,
        domain.domain_name,
        data.client_id,
    )
    notifications.notify_domain_registered(db, domain)
    return domain


@router.get("", response_model=list[DomainListItem], summary="List domains (ADMIN or STAFF)")
def list_domains(
    db: DbDep,
    current_user: StaffOrAdmin,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: DomainStatus | None = None,
    client_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    return domain_crud.list_domains(
        db,
        limit=limit,
        offset=offset,
        status=status,
        client_id=client_id,
        search=search,
        include_inactive=include_inactive,
    )


# --- domain extensions (price list) ----------------------------------------
#
# Admin-managed per-TLD pricing. The public endpoint drives the price table
# shown on the Domains page; the write endpoints are admin-only, like the
# hosting-plans module next door.


@router.get(
    "/extensions",
    response_model=list[DomainExtensionRead],
    summary="List active domain extensions with computed client prices (public)",
)
def list_domain_extensions(db: DbDep):
    """
    Open, because the public Domains page shows a price table and the quote
    form may reference it. Only active rows come back; staff manage soft-deleted
    ones through the dedicated admin endpoint below.
    """
    return extension_crud.list_extensions(db)


@router.get(
    "/extensions/manage",
    response_model=list[DomainExtensionRead],
    dependencies=[Depends(require_roles(Role.ADMIN))],
    summary="List every extension including soft-deleted ones (ADMIN only)",
)
def list_all_domain_extensions(db: DbDep, include_inactive: bool = True):
    return extension_crud.list_extensions(db, include_inactive=include_inactive)


@router.post(
    "/extensions",
    response_model=DomainExtensionRead,
    status_code=201,
    summary="Add a domain extension (ADMIN only)",
)
def create_domain_extension(
    data: DomainExtensionCreate, db: DbDep, admin: AdminOnly
):
    """
    Rejected with a 409 if the extension already exists -- there is one row
    per TLD by construction, and silently replacing an admin's price would be
    worse than making them look it up.
    """
    if extension_crud.get_by_extension(db, data.extension) is not None:
        raise HTTPException(
            status_code=409, detail=f"Extension {data.extension} already exists"
        )
    row = extension_crud.create(db, data)
    logger.info("admin %s added domain extension %s", admin.id, row.extension)
    return row


@router.patch(
    "/extensions/{extension_id}",
    response_model=DomainExtensionRead,
    summary="Edit a domain extension (ADMIN only)",
)
def update_domain_extension(
    extension_id: int,
    data: DomainExtensionUpdate,
    db: DbDep,
    admin: AdminOnly,
):
    row = extension_crud.get_by_id(db, extension_id)
    if not row:
        raise HTTPException(status_code=404, detail="Extension not found")
    updated = extension_crud.update(db, row, data)
    logger.info(
        "admin %s edited domain extension %s: %s",
        admin.id,
        extension_id,
        data.model_dump(exclude_unset=True),
    )
    return updated


@router.delete(
    "/extensions/{extension_id}",
    response_model=DomainExtensionRead,
    summary="Soft-delete a domain extension (ADMIN only)",
)
def deactivate_domain_extension(extension_id: int, db: DbDep, admin: AdminOnly):
    row = extension_crud.get_by_id(db, extension_id)
    if not row:
        raise HTTPException(status_code=404, detail="Extension not found")
    updated = extension_crud.deactivate(db, row)
    logger.info("admin %s deactivated domain extension %s", admin.id, extension_id)
    return updated


@router.get("/{domain_id}", response_model=DomainRead, summary="Get a domain (ADMIN or STAFF)")
def get_domain(domain_id: int, db: DbDep, current_user: StaffOrAdmin):
    domain = domain_crud.get_domain(db, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain


@router.patch("/{domain_id}", response_model=DomainRead, summary="Update a domain (ADMIN or STAFF)")
def update_domain(domain_id: int, data: DomainUpdate, db: DbDep, current_user: StaffOrAdmin):
    domain = domain_crud.get_domain(db, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    validate_settable_status(data.status)
    if "hosting_account_id" in data.model_fields_set and data.hosting_account_id is not None:
        validate_hosting_account(db, data.hosting_account_id, domain.client_id)

    # Captured before the update mutates the row in place.
    old_status = domain.status
    updated = domain_crud.update_domain(db, domain, data)
    logger.info(
        "staff %s updated domain %s: %s",
        current_user.id,
        domain_id,
        data.model_dump(exclude_unset=True),
    )

    # Only a real transition into a notifiable state is an event.
    if updated.status != old_status and updated.status in NOTIFIABLE_STATUSES:
        notifications.notify_domain_status_changed(db, updated)
    return updated


@router.delete(
    "/{domain_id}",
    response_model=DomainRead,
    summary="Deactivate a domain record (ADMIN only, soft delete)",
)
def deactivate_domain(domain_id: int, db: DbDep, admin: AdminOnly):
    domain = domain_crud.get_domain(db, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    updated = domain_crud.deactivate_domain(db, domain)
    logger.info("admin %s deactivated domain %s", admin.id, domain_id)
    return updated
