import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, DbDep, require_roles
from app.crud import project as project_crud
from app.crud import service as service_crud
from app.crud import user as user_crud
from app.models.project import Project, ProjectPriority, ProjectStatus
from app.models.quote_request import QuoteRequest, QuoteStatus
from app.models.user import Role, User
from app.schemas.project import ProjectCreate, ProjectListItem, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]


def validate_client_for_project(db: Session, client_id: int) -> None:
    client = user_crud.get_by_id(db, client_id)
    if not client or not client.is_active or client.role != Role.CLIENT:
        raise HTTPException(
            status_code=422,
            detail="client_id must reference an active user with the CLIENT role",
        )


def validate_service_for_project(db: Session, service_id: int) -> None:
    service = service_crud.get_by_id(db, service_id)
    if not service or not service.is_active:
        raise HTTPException(
            status_code=422, detail="service_id does not reference an active service"
        )


def get_valid_quote_for_linking(db: Session, quote_id: int) -> QuoteRequest:
    """Fetch `quote_id` and raise unless it is eligible to be linked to a new project."""
    quote = db.get(QuoteRequest, quote_id)
    if not quote or not quote.is_active:
        raise HTTPException(
            status_code=422,
            detail="quote_request_id does not reference an active quote request",
        )
    if quote.status != QuoteStatus.ACCEPTED:
        raise HTTPException(
            status_code=422,
            detail="Quote request must be ACCEPTED before it can be linked to a project",
        )
    if project_crud.get_by_quote_request_id(db, quote.id) is not None:
        raise HTTPException(
            status_code=409, detail="This quote request is already linked to a project"
        )
    return quote


def _validate_update_dates(project: Project, data: ProjectUpdate) -> None:
    fields = data.model_fields_set
    start = data.start_date if "start_date" in fields else project.start_date
    deadline = data.deadline if "deadline" in fields else project.deadline
    if start and deadline and deadline < start:
        raise HTTPException(status_code=422, detail="deadline cannot be before start_date")


def project_visible_to(current_user: User, project: Project) -> bool:
    if current_user.role in (Role.ADMIN, Role.STAFF):
        return True
    return project.client_id == current_user.id


@router.post(
    "",
    response_model=ProjectRead,
    status_code=201,
    summary="Create a project (ADMIN or STAFF only)",
)
def create_project(data: ProjectCreate, db: DbDep, current_user: StaffOrAdmin):
    validate_client_for_project(db, data.client_id)
    if data.service_id is not None:
        validate_service_for_project(db, data.service_id)
    if data.quote_request_id is not None:
        get_valid_quote_for_linking(db, data.quote_request_id)

    project = project_crud.create(db, data)
    logger.info(
        "staff %s created project %s for client %s", current_user.id, project.id, data.client_id
    )
    return project


@router.get("", response_model=list[ProjectListItem], summary="List projects (role-scoped)")
def list_projects(
    db: DbDep,
    current_user: ActiveUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: ProjectStatus | None = None,
    priority: ProjectPriority | None = None,
    service_id: int | None = None,
    client_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    if current_user.role == Role.CLIENT:
        client_id = current_user.id
        include_inactive = False
    return project_crud.list_projects(
        db,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        service_id=service_id,
        client_id=client_id,
        search=search,
        include_inactive=include_inactive,
    )


@router.get("/{project_id}", response_model=ProjectRead, summary="Get a single project")
def get_project(project_id: int, db: DbDep, current_user: ActiveUser):
    project = project_crud.get_by_id(db, project_id)
    if not project or not project_visible_to(current_user, project):
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.role == Role.CLIENT and not project.is_active:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update a project (ADMIN or STAFF only)",
)
def update_project(project_id: int, data: ProjectUpdate, db: DbDep, current_user: StaffOrAdmin):
    project = project_crud.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    _validate_update_dates(project, data)
    updated = project_crud.update(db, project, data)
    logger.info(
        "staff %s updated project %s: %s",
        current_user.id,
        project_id,
        data.model_dump(exclude_unset=True),
    )
    return updated


@router.delete(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Deactivate a project (ADMIN only, soft delete)",
)
def deactivate_project(project_id: int, db: DbDep, current_user: AdminOnly):
    project = project_crud.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = project_crud.deactivate(db, project)
    logger.info("admin %s deactivated project %s", current_user.id, project_id)
    return updated
