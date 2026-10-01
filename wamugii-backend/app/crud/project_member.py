from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectRole


def get_by_id_for_project(
    db: Session, member_id: int, project_id: int
) -> ProjectMember | None:
    """Scoped lookup: a member id from another project reads as missing (404)."""
    return db.scalar(
        select(ProjectMember).where(
            ProjectMember.id == member_id, ProjectMember.project_id == project_id
        )
    )


def get_membership(db: Session, project_id: int, user_id: int) -> ProjectMember | None:
    """The row for this pairing whether or not it is active."""
    return db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    )


def list_for_project(
    db: Session, project_id: int, *, include_inactive: bool = False
) -> list[ProjectMember]:
    query = select(ProjectMember).where(ProjectMember.project_id == project_id)
    if not include_inactive:
        query = query.where(ProjectMember.is_active.is_(True))
    return list(db.scalars(query.order_by(ProjectMember.id)).all())


def add_or_reactivate(
    db: Session,
    *,
    project_id: int,
    user_id: int,
    project_role: ProjectRole,
    assigned_by: int,
) -> tuple[ProjectMember, bool]:
    """
    Assign `user_id` to `project_id`.

    Returns `(member, is_new_assignment)`. The unique constraint on
    (project_id, user_id) means a previously removed member cannot be inserted
    again, so their existing row is reactivated with the new role instead --
    which keeps the original `assigned_at` as the record of when they first
    joined. `is_new_assignment` is False when the row was already active, so
    the caller can skip re-notifying someone who is simply changing role.
    """
    existing = get_membership(db, project_id, user_id)
    if existing is not None:
        was_active = existing.is_active
        existing.project_role = project_role
        existing.is_active = True
        existing.assigned_by = assigned_by
        db.commit()
        db.refresh(existing)
        return existing, not was_active

    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        project_role=project_role,
        assigned_by=assigned_by,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member, True


def update_role(
    db: Session, member: ProjectMember, project_role: ProjectRole
) -> ProjectMember:
    member.project_role = project_role
    db.commit()
    db.refresh(member)
    return member


def deactivate(db: Session, member: ProjectMember) -> ProjectMember:
    member.is_active = False
    db.commit()
    db.refresh(member)
    return member


# --- the team member's own view --------------------------------------------


def is_active_member(db: Session, project_id: int, user_id: int) -> bool:
    """The single predicate behind every team-member access check."""
    return (
        db.scalar(
            select(func.count())
            .select_from(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active.is_(True),
            )
        )
        or 0
    ) > 0


def list_projects_for_member(
    db: Session, user_id: int
) -> list[tuple[Project, ProjectRole]]:
    """
    Active projects this user is an active member of, with their role on each.

    Both flags matter: removing a member and deactivating a project each have
    to take the project out of the member's list.
    """
    rows = db.execute(
        select(Project, ProjectMember.project_role)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(
            ProjectMember.user_id == user_id,
            ProjectMember.is_active.is_(True),
            Project.is_active.is_(True),
        )
        .order_by(Project.id.desc())
    ).all()
    return [(project, role) for project, role in rows]


def get_project_for_member(
    db: Session, project_id: int, user_id: int
) -> tuple[Project, ProjectRole] | None:
    """One project plus the caller's role, or None -- the caller raises 404."""
    row = db.execute(
        select(Project, ProjectMember.project_role)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(
            Project.id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.is_active.is_(True),
            Project.is_active.is_(True),
        )
    ).first()
    if row is None:
        return None
    project, role = row
    return project, role
