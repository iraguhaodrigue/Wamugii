from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectPriority, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_by_quote_request_id(db: Session, quote_request_id: int) -> Project | None:
    return db.scalar(
        select(Project).where(
            Project.quote_request_id == quote_request_id, Project.is_active.is_(True)
        )
    )


def list_projects(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    status: ProjectStatus | None = None,
    priority: ProjectPriority | None = None,
    service_id: int | None = None,
    client_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[Project]:
    query = select(Project)
    if not include_inactive:
        query = query.where(Project.is_active.is_(True))
    if status is not None:
        query = query.where(Project.status == status)
    if priority is not None:
        query = query.where(Project.priority == priority)
    if service_id is not None:
        query = query.where(Project.service_id == service_id)
    if client_id is not None:
        query = query.where(Project.client_id == client_id)
    if search:
        term = search.lower()
        query = query.where(func.lower(Project.title).contains(term))
    query = query.order_by(Project.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def create(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump(), status=ProjectStatus.PENDING)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update(db: Session, project: Project, data: ProjectUpdate) -> Project:
    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        if updates["status"] == ProjectStatus.COMPLETED:
            if project.completed_at is None:
                updates["completed_at"] = datetime.now(timezone.utc)
        else:
            updates["completed_at"] = None
    for field, value in updates.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def deactivate(db: Session, project: Project) -> Project:
    project.is_active = False
    db.commit()
    db.refresh(project)
    return project


def count_total(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Project)) or 0


def count_active(db: Session) -> int:
    return (
        db.scalar(select(func.count()).select_from(Project).where(Project.is_active.is_(True)))
        or 0
    )
