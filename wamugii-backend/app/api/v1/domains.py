import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.crud import domain as domain_crud
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
