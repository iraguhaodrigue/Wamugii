import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, DbDep, require_roles
from app.crud import project as project_crud
from app.crud import project_milestone as milestone_crud
from app.models.project_milestone import MilestoneStatus, ProjectMilestone
from app.models.user import Role, User
from app.schemas.project_milestone import (
    ProjectMilestoneCreate,
    ProjectMilestoneListItem,
    ProjectMilestoneRead,
    ProjectMilestoneUpdate,
    ProjectProgressRead,
)

router = APIRouter(prefix="/projects", tags=["project-milestones"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]
AdminOnly = Annotated[User, Depends(require_roles(Role.ADMIN))]


def _milestone_visible_to(current_user: User, project_id: int, db: Session) -> bool:
    """Check if user can view milestones for the given project."""
    if current_user.role in (Role.ADMIN, Role.STAFF):
        return True
    # CLIENT can only view milestones for their own projects
    project = project_crud.get_by_id(db, project_id)
    if not project:
        return False
    return project.client_id == current_user.id


def _project_exists_and_active(db: Session, project_id: int) -> bool:
    """Verify project exists and is active."""
    project = project_crud.get_by_id(db, project_id)
    return project is not None and project.is_active


def _validate_milestone_for_update_dates(
    milestone, data: ProjectMilestoneUpdate
) -> None:
    """Validate date constraints for milestone update."""
    fields = data.model_fields_set
    start = data.start_date if "start_date" in fields else milestone.start_date
    due = data.due_date if "due_date" in fields else milestone.due_date
    if start and due and due < start:
        raise HTTPException(status_code=422, detail="due_date cannot be before start_date")


class MilestoneReorderItem(BaseModel):
    id: int
    display_order: int


class MilestoneReorderRequest(BaseModel):
    milestones: list[MilestoneReorderItem]


@router.post(
    "/{project_id}/milestones",
    response_model=ProjectMilestoneRead,
    status_code=201,
    summary="Create a milestone (ADMIN or STAFF only)",
)
def create_milestone(
    project_id: int,
    data: ProjectMilestoneCreate,
    db: DbDep,
    current_user: StaffOrAdmin,
):
    """Create a new milestone for a project."""
    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    milestone = milestone_crud.create(db, project_id, data)
    logger.info(
        "staff %s created milestone %s for project %s",
        current_user.id,
        milestone.id,
        project_id,
    )
    return milestone


@router.get(
    "/{project_id}/milestones",
    response_model=list[ProjectMilestoneListItem],
    summary="List project milestones (role-scoped)",
)
def list_milestones(
    project_id: int,
    db: DbDep,
    current_user: ActiveUser,
    status: MilestoneStatus | None = None,
    include_inactive: bool = False,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List milestones for a project with authorization checks."""
    if not _milestone_visible_to(current_user, project_id, db):
        raise HTTPException(status_code=404, detail="Project not found")

    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    # CLIENT cannot see inactive milestones
    if current_user.role == Role.CLIENT:
        include_inactive = False

    return milestone_crud.list_milestones(
        db,
        project_id,
        limit=limit,
        offset=offset,
        status=status,
        include_inactive=include_inactive,
    )


@router.patch(
    "/{project_id}/milestones/reorder",
    summary="Reorder milestones (ADMIN or STAFF only)",
)
def reorder_milestones(
    project_id: int,
    request: MilestoneReorderRequest,
    db: DbDep,
    current_user: StaffOrAdmin,
):
    """Reorder milestones using a transaction."""
    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    # Validate all milestones belong to the project and exist
    milestone_ids = {item.id for item in request.milestones}
    milestones = milestone_crud.list_milestones(
        db, project_id, limit=1000, include_inactive=True
    )
    existing_ids = {m.id for m in milestones}

    # Check for invalid milestone IDs
    invalid_ids = milestone_ids - existing_ids
    if invalid_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Milestones with ids {invalid_ids} do not belong to this project",
        )

    try:
        # Update display orders in transaction
        for item in request.milestones:
            milestone = db.get(ProjectMilestone, item.id)
            if milestone and milestone.project_id == project_id:
                milestone.display_order = item.display_order
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(
            "Error reordering milestones for project %s: %s",
            project_id,
            str(e),
        )
        raise HTTPException(
            status_code=500, detail="Failed to reorder milestones"
        ) from e

    logger.info(
        "staff %s reordered milestones for project %s",
        current_user.id,
        project_id,
    )

    return {"message": "Milestones reordered successfully"}


@router.get(
    "/{project_id}/milestones/{milestone_id}",
    response_model=ProjectMilestoneRead,
    summary="Get a single milestone",
)
def get_milestone(
    project_id: int,
    milestone_id: int,
    db: DbDep,
    current_user: ActiveUser,
):
    """Get a single milestone with authorization checks."""
    if not _milestone_visible_to(current_user, project_id, db):
        raise HTTPException(status_code=404, detail="Project not found")

    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    milestone = milestone_crud.get_by_id_for_project(db, milestone_id, project_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    if current_user.role == Role.CLIENT and not milestone.is_active:
        raise HTTPException(status_code=404, detail="Milestone not found")

    return milestone


@router.patch(
    "/{project_id}/milestones/{milestone_id}",
    response_model=ProjectMilestoneRead,
    summary="Update a milestone (ADMIN or STAFF only)",
)
def update_milestone(
    project_id: int,
    milestone_id: int,
    data: ProjectMilestoneUpdate,
    db: DbDep,
    current_user: StaffOrAdmin,
):
    """Update a milestone with validation."""
    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    milestone = milestone_crud.get_by_id_for_project(db, milestone_id, project_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    _validate_milestone_for_update_dates(milestone, data)
    updated = milestone_crud.update(db, milestone, data)

    logger.info(
        "staff %s updated milestone %s for project %s: %s",
        current_user.id,
        milestone_id,
        project_id,
        data.model_dump(exclude_unset=True),
    )
    return updated


@router.delete(
    "/{project_id}/milestones/{milestone_id}",
    response_model=ProjectMilestoneRead,
    summary="Soft-delete a milestone (ADMIN only)",
)
def deactivate_milestone(
    project_id: int,
    milestone_id: int,
    db: DbDep,
    current_user: AdminOnly,
):
    """Soft-delete (deactivate) a milestone."""
    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    milestone = milestone_crud.get_by_id_for_project(db, milestone_id, project_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    updated = milestone_crud.deactivate(db, milestone)
    logger.info(
        "admin %s deactivated milestone %s for project %s",
        current_user.id,
        milestone_id,
        project_id,
    )
    return updated


@router.get(
    "/{project_id}/progress",
    response_model=ProjectProgressRead,
    summary="Get project progress",
)
def get_project_progress(
    project_id: int,
    db: DbDep,
    current_user: ActiveUser,
):
    """Calculate and return project progress based on milestones."""
    if not _milestone_visible_to(current_user, project_id, db):
        raise HTTPException(status_code=404, detail="Project not found")

    if not _project_exists_and_active(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found or is inactive")

    progress = milestone_crud.get_project_progress(db, project_id)
    return progress
