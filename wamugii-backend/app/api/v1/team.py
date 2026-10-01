"""
The team member's own view.

This is the *entire* read surface a TEAM_MEMBER is given. Three things keep the
privacy wall standing, and all three are deliberate:

1. Scope -- every query goes through `crud.project_member`, which joins on an
   active membership, so a project the caller isn't on simply isn't in the
   result set. Anything else is a 404, never a 403, matching the convention
   used for projects, milestones and tickets.
2. Shape -- responses are built from `schemas/team.py`, whose models declare no
   client or billing field, so there is nothing to leak even if `Project` grows
   new columns later.
3. Everything else is shut -- `/projects`, its milestones and its files read
   through `deps.NonTeamUser`, and every other module is gated by
   `require_roles`, which TEAM_MEMBER is in none of.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from app.api.deps import DbDep, require_roles
from app.crud import project_file as file_crud
from app.crud import project_member as member_crud
from app.crud import project_milestone as milestone_crud
from app.models.user import Role, User
from app.schemas.team import (
    TeamProjectDetail,
    TeamProjectFile,
    TeamProjectListItem,
    TeamProjectMilestone,
)
from app.services import storage

router = APIRouter(prefix="/team", tags=["team"])
logger = logging.getLogger(__name__)

TeamMemberOnly = Annotated[User, Depends(require_roles(Role.TEAM_MEMBER))]


@router.get(
    "/projects",
    response_model=list[TeamProjectListItem],
    summary="List the projects the authenticated TEAM_MEMBER is assigned to",
)
def list_my_projects(
    db: DbDep,
    current_user: TeamMemberOnly,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    rows = member_crud.list_projects_for_member(db, current_user.id)
    page = rows[offset : offset + limit]
    return [
        TeamProjectListItem(
            id=project.id,
            title=project.title,
            status=project.status,
            priority=project.priority,
            deadline=project.deadline,
            created_at=project.created_at,
            my_role=role,
        )
        for project, role in page
    ]


@router.get(
    "/projects/{project_id}",
    response_model=TeamProjectDetail,
    summary="Get one assigned project with its milestones and files",
)
def get_my_project(project_id: int, db: DbDep, current_user: TeamMemberOnly):
    """404 for anything that isn't an active project they're an active member of."""
    found = member_crud.get_project_for_member(db, project_id, current_user.id)
    if found is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project, role = found

    # Explicit limits: list_files defaults to 20, which would silently truncate
    # the file list on a busy project.
    milestones = milestone_crud.list_milestones(
        db, project_id=project.id, limit=100, include_inactive=False
    )
    files = file_crud.list_files(
        db, project_id=project.id, limit=100, include_inactive=False
    )

    return TeamProjectDetail(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        priority=project.priority,
        start_date=project.start_date,
        deadline=project.deadline,
        completed_at=project.completed_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
        my_role=role,
        milestones=[TeamProjectMilestone.model_validate(m) for m in milestones],
        files=[TeamProjectFile.model_validate(f) for f in files],
    )


@router.get(
    "/projects/{project_id}/files/{file_id}/download",
    summary="Download a file on an assigned project",
)
def download_my_project_file(
    project_id: int, file_id: int, db: DbDep, current_user: TeamMemberOnly
):
    """
    Mirrors `project_files.download_file`, scoped to membership.

    Here rather than on the existing route because that one is closed to team
    members: this keeps the whole team-member surface inside /team, which is
    the only place the privacy rules have to be audited. Without it the file
    list on the detail page would be metadata nobody can open.
    """
    if member_crud.get_project_for_member(db, project_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Project not found")

    file = file_crud.get_by_id_for_project(db, file_id, project_id)
    if not file or not file.is_active:
        raise HTTPException(status_code=404, detail="File not found")

    physical_path = storage.get_file(file.storage_path)
    if not physical_path.is_file():
        logger.error("Physical file missing for project_file %s at %s", file.id, physical_path)
        raise HTTPException(status_code=404, detail="File content not found")

    return FileResponse(
        path=physical_path,
        media_type=file.content_type,
        filename=file.original_filename,
    )
