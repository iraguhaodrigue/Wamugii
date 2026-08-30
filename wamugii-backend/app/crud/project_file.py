from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.project_file import FileCategory, ProjectFile
from app.schemas.project_file import ProjectFileUpdate


def get_by_id(db: Session, file_id: int) -> ProjectFile | None:
    return db.get(ProjectFile, file_id)


def get_by_id_for_project(db: Session, file_id: int, project_id: int) -> ProjectFile | None:
    return db.scalar(
        select(ProjectFile).where(
            and_(
                ProjectFile.id == file_id,
                ProjectFile.project_id == project_id,
            )
        )
    )


def list_files(
    db: Session,
    project_id: int,
    *,
    limit: int = 20,
    offset: int = 0,
    category: FileCategory | None = None,
    include_inactive: bool = False,
) -> list[ProjectFile]:
    query = select(ProjectFile).where(ProjectFile.project_id == project_id)

    if not include_inactive:
        query = query.where(ProjectFile.is_active.is_(True))

    if category is not None:
        query = query.where(ProjectFile.category == category)

    query = (
        query.order_by(ProjectFile.created_at.desc(), ProjectFile.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(query).all())


def create(
    db: Session,
    *,
    project_id: int,
    uploaded_by: int,
    original_filename: str,
    stored_filename: str,
    storage_path: str,
    content_type: str,
    file_size: int,
    category: FileCategory,
    description: str | None,
) -> ProjectFile:
    file = ProjectFile(
        project_id=project_id,
        uploaded_by=uploaded_by,
        original_filename=original_filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        content_type=content_type,
        file_size=file_size,
        category=category,
        description=description,
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def update_metadata(db: Session, file: ProjectFile, data: ProjectFileUpdate) -> ProjectFile:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(file, field, value)
    db.commit()
    db.refresh(file)
    return file


def deactivate(db: Session, file: ProjectFile) -> ProjectFile:
    file.is_active = False
    db.commit()
    db.refresh(file)
    return file
