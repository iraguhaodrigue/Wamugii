from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_milestone import MilestoneStatus, ProjectMilestone
from app.schemas.project_milestone import ProjectMilestoneCreate, ProjectMilestoneUpdate


def get_by_id(db: Session, milestone_id: int) -> ProjectMilestone | None:
    return db.get(ProjectMilestone, milestone_id)


def get_by_id_for_project(
    db: Session, milestone_id: int, project_id: int
) -> ProjectMilestone | None:
    return db.scalar(
        select(ProjectMilestone).where(
            and_(
                ProjectMilestone.id == milestone_id,
                ProjectMilestone.project_id == project_id,
            )
        )
    )


def list_milestones(
    db: Session,
    project_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
    status: MilestoneStatus | None = None,
    include_inactive: bool = False,
) -> list[ProjectMilestone]:
    query = select(ProjectMilestone).where(ProjectMilestone.project_id == project_id)

    if not include_inactive:
        query = query.where(ProjectMilestone.is_active.is_(True))

    if status is not None:
        query = query.where(ProjectMilestone.status == status)

    query = (
        query.order_by(ProjectMilestone.display_order.asc())
        .order_by(ProjectMilestone.created_at.asc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(query).all())


def create(db: Session, project_id: int, data: ProjectMilestoneCreate) -> ProjectMilestone:
    # If display_order is not provided, assign it as the next order
    display_order = data.display_order
    if display_order is None:
        max_order = db.scalar(
            select(func.max(ProjectMilestone.display_order)).where(
                ProjectMilestone.project_id == project_id
            )
        )
        display_order = (max_order or 0) + 1

    milestone = ProjectMilestone(
        project_id=project_id,
        title=data.title,
        description=data.description,
        status=data.status,
        display_order=display_order,
        start_date=data.start_date,
        due_date=data.due_date,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def update(
    db: Session, milestone: ProjectMilestone, data: ProjectMilestoneUpdate
) -> ProjectMilestone:
    updates = data.model_dump(exclude_unset=True)

    # Handle completed_at based on status changes
    if "status" in updates:
        if updates["status"] == MilestoneStatus.COMPLETED:
            if milestone.completed_at is None:
                updates["completed_at"] = datetime.now(timezone.utc)
        elif milestone.status == MilestoneStatus.COMPLETED and updates["status"] != MilestoneStatus.COMPLETED:
            # Moving away from COMPLETED: clear completed_at
            updates["completed_at"] = None

    for field, value in updates.items():
        setattr(milestone, field, value)

    db.commit()
    db.refresh(milestone)
    return milestone


def deactivate(db: Session, milestone: ProjectMilestone) -> ProjectMilestone:
    milestone.is_active = False
    db.commit()
    db.refresh(milestone)
    return milestone


def get_project_progress(db: Session, project_id: int) -> dict:
    """Calculate project progress based on active milestones."""
    query = select(ProjectMilestone).where(
        and_(
            ProjectMilestone.project_id == project_id,
            ProjectMilestone.is_active.is_(True),
        )
    )
    milestones = list(db.scalars(query).all())

    total = len(milestones)
    completed = sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)
    in_progress = sum(1 for m in milestones if m.status == MilestoneStatus.IN_PROGRESS)
    pending = sum(1 for m in milestones if m.status == MilestoneStatus.PENDING)

    progress_percentage = (completed / total * 100) if total > 0 else 0.0

    return {
        "project_id": project_id,
        "total_milestones": total,
        "completed_milestones": completed,
        "in_progress_milestones": in_progress,
        "pending_milestones": pending,
        "progress_percentage": round(progress_percentage, 2),
    }
