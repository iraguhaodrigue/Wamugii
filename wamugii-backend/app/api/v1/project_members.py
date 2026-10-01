import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import DbDep, require_roles
from app.crud import project as project_crud
from app.crud import project_member as member_crud
from app.crud import user as user_crud
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import ApprovalStatus, Role, User
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberRead,
    ProjectMemberUpdate,
)
from app.services import notifications

router = APIRouter(prefix="/projects", tags=["project-members"])
logger = logging.getLogger(__name__)

StaffOrAdmin = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STAFF))]

# Who may be put on a project. A CLIENT is the other side of the relationship
# and an ADMIN doesn't need a membership row to see everything, so neither is
# assignable -- allowing it would also mean a client turning up in a team
# member's colleague list.
ASSIGNABLE_ROLES = (Role.TEAM_MEMBER, Role.STAFF)


def _get_project(db: Session, project_id: int) -> Project:
    project = project_crud.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def validate_assignable_user(db: Session, user_id: int) -> User:
    user = user_crud.get_by_id(db, user_id)
    if (
        not user
        or not user.is_active
        or user.role not in ASSIGNABLE_ROLES
        or user.approval_status != ApprovalStatus.APPROVED
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "user_id must reference an active, approved user with the "
                "TEAM_MEMBER or STAFF role"
            ),
        )
    return user


def _with_user(db: Session, member: ProjectMember) -> ProjectMemberRead:
    """Attach the member's identity for the staff-facing response."""
    read = ProjectMemberRead.model_validate(member)
    user = user_crud.get_by_id(db, member.user_id)
    if user is not None:
        read.user_full_name = user.full_name
        read.user_email = user.email
        read.user_role = user.role.value
    return read


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberRead,
    status_code=201,
    summary="Assign a user to a project with a role (ADMIN or STAFF)",
)
def add_member(
    project_id: int,
    data: ProjectMemberCreate,
    db: DbDep,
    current_user: StaffOrAdmin,
):
    """
    Assign, or re-assign, a user to this project.

    Re-adding someone who was previously removed reactivates their existing
    membership rather than creating a second row -- see
    `crud.project_member.add_or_reactivate`. Only a genuinely new assignment
    notifies; changing the role of an already-active member does not, so a
    typo-correction doesn't email them twice.
    """
    project = _get_project(db, project_id)
    user = validate_assignable_user(db, data.user_id)

    member, is_new = member_crud.add_or_reactivate(
        db,
        project_id=project.id,
        user_id=user.id,
        project_role=data.project_role,
        assigned_by=current_user.id,
    )
    logger.info(
        "staff %s assigned user %s to project %s as %s",
        current_user.id,
        user.id,
        project.id,
        data.project_role.value,
    )
    if is_new:
        notifications.notify_project_assignment(db, member, project, user)
    return _with_user(db, member)


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberRead],
    summary="List a project's members (ADMIN or STAFF)",
)
def list_members(
    project_id: int,
    db: DbDep,
    current_user: StaffOrAdmin,
    include_inactive: bool = False,
):
    _get_project(db, project_id)
    members = member_crud.list_for_project(
        db, project_id, include_inactive=include_inactive
    )
    return [_with_user(db, m) for m in members]


@router.patch(
    "/{project_id}/members/{member_id}",
    response_model=ProjectMemberRead,
    summary="Change a member's project role (ADMIN or STAFF)",
)
def update_member(
    project_id: int,
    member_id: int,
    data: ProjectMemberUpdate,
    db: DbDep,
    current_user: StaffOrAdmin,
):
    _get_project(db, project_id)
    member = member_crud.get_by_id_for_project(db, member_id, project_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")

    updated = member_crud.update_role(db, member, data.project_role)
    logger.info(
        "staff %s changed member %s on project %s to %s",
        current_user.id,
        member_id,
        project_id,
        data.project_role.value,
    )
    return _with_user(db, updated)


@router.delete(
    "/{project_id}/members/{member_id}",
    response_model=ProjectMemberRead,
    summary="Remove a member from a project (ADMIN or STAFF, soft delete)",
)
def remove_member(
    project_id: int,
    member_id: int,
    db: DbDep,
    current_user: StaffOrAdmin,
):
    """
    Soft delete. The row stays so the assignment history survives, and the
    project drops out of that member's /team/projects immediately.
    """
    _get_project(db, project_id)
    member = member_crud.get_by_id_for_project(db, member_id, project_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")

    updated = member_crud.deactivate(db, member)
    logger.info("staff %s removed member %s from project %s", current_user.id, member_id, project_id)
    return _with_user(db, updated)
