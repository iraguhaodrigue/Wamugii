import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DbDep, require_roles
from app.api.v1.projects import (
    get_valid_quote_for_linking,
    validate_client_for_project,
    validate_service_for_project,
)
from app.crud import project as project_crud
from app.crud import quote_request as quote_crud
from app.crud import service as service_crud
from app.crud import user as user_crud
from app.models.quote_request import QuoteStatus
from app.models.user import Role, User
from app.schemas.project import ProjectCreate, ProjectRead
from app.schemas.quote_request import (
    QuoteRequestAdminUpdate,
    QuoteRequestCreate,
    QuoteRequestPublicRead,
    QuoteRequestRead,
)
from app.services import notifications

router = APIRouter(prefix="/quote-requests", tags=["quote-requests"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]


@router.post(
    "",
    response_model=QuoteRequestPublicRead,
    status_code=201,
    summary="Submit a quote request (public, no account needed)",
)
def create_quote_request(data: QuoteRequestCreate, db: DbDep):
    if data.service_id is not None:
        service = service_crud.get_by_id(db, data.service_id)
        if not service or not service.is_active:
            raise HTTPException(
                status_code=422, detail="service_id does not reference an active service"
            )
    quote = quote_crud.create(db, data)
    # After the commit, and non-fatal: a notification failure must not turn a
    # successfully submitted quote into an error for the public submitter.
    notifications.notify_quote_submitted(db, quote)
    return quote


@router.get(
    "",
    response_model=list[QuoteRequestRead],
    summary="List quote requests (ADMIN or STAFF only)",
)
def list_quote_requests(
    db: DbDep,
    current_user: StaffOrAdmin,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: QuoteStatus | None = None,
    service_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    return quote_crud.list_quote_requests(
        db,
        limit=limit,
        offset=offset,
        status=status,
        service_id=service_id,
        search=search,
        include_inactive=include_inactive,
    )


@router.get(
    "/{quote_id}",
    response_model=QuoteRequestRead,
    summary="Get a quote request (ADMIN or STAFF only)",
)
def get_quote_request(quote_id: int, db: DbDep, current_user: StaffOrAdmin):
    quote = quote_crud.get_by_id(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote request not found")
    return quote


@router.patch(
    "/{quote_id}",
    response_model=QuoteRequestRead,
    summary="Update quote status and/or admin notes (ADMIN or STAFF only)",
)
def update_quote_request(
    quote_id: int, data: QuoteRequestAdminUpdate, db: DbDep, current_user: StaffOrAdmin
):
    quote = quote_crud.get_by_id(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote request not found")
    # Captured before the update mutates the row in place.
    old_status = quote.status
    updated = quote_crud.update_admin_fields(db, quote, data)
    logger.info(
        "staff %s updated quote %s: %s",
        current_user.id,
        quote_id,
        data.model_dump(exclude_unset=True),
    )
    # Only a real transition is worth notifying about — a notes-only edit isn't.
    if updated.status != old_status:
        notifications.notify_quote_status_changed(db, updated, old_status.value)
    return updated


@router.delete(
    "/{quote_id}",
    response_model=QuoteRequestRead,
    summary="Soft-delete a quote request (ADMIN only)",
)
def delete_quote_request(quote_id: int, db: DbDep, current_user: AdminOnly):
    quote = quote_crud.get_by_id(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote request not found")
    updated = quote_crud.soft_delete(db, quote)
    logger.info("admin %s soft-deleted quote %s", current_user.id, quote_id)
    return updated


@router.post(
    "/{quote_id}/create-project",
    response_model=ProjectRead,
    status_code=201,
    tags=["projects"],
    summary="Convert an ACCEPTED quote request into a project (ADMIN or STAFF only)",
)
def create_project_from_quote(
    quote_id: int,
    db: DbDep,
    current_user: StaffOrAdmin,
    client_id: int | None = Query(
        None,
        description=(
            "User id of the client who owns the resulting project. If omitted, an active "
            "CLIENT account matching the quote's email is used; required if none matches "
            "(quote requests don't require an account, so there may be no automatic match)."
        ),
    ),
):
    quote = quote_crud.get_by_id(db, quote_id)
    if not quote or not quote.is_active:
        raise HTTPException(status_code=404, detail="Quote request not found")
    get_valid_quote_for_linking(db, quote_id)

    resolved_client_id = client_id
    if resolved_client_id is None:
        matching_client = user_crud.get_by_email(db, quote.email.lower())
        if matching_client is not None:
            resolved_client_id = matching_client.id
    if resolved_client_id is None:
        raise HTTPException(
            status_code=422,
            detail=(
                f"No client_id given and no user account matches this quote's email "
                f"({quote.email}). Pass ?client_id=<user_id>, or create/activate that "
                "client's account first."
            ),
        )
    validate_client_for_project(db, resolved_client_id)

    if quote.service_id is not None:
        validate_service_for_project(db, quote.service_id)

    project_data = ProjectCreate(
        client_id=resolved_client_id,
        quote_request_id=quote.id,
        service_id=quote.service_id,
        title=quote.project_title,
        description=quote.project_description,
    )
    project = project_crud.create(db, project_data)
    logger.info(
        "staff %s converted quote %s into project %s", current_user.id, quote_id, project.id
    )
    notifications.notify_project_created(db, project)
    return project
