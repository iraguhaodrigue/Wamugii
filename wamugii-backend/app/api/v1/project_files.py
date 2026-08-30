import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, DbDep
from app.core.config import settings
from app.crud import project as project_crud
from app.crud import project_file as file_crud
from app.models.project import Project
from app.models.project_file import FileCategory
from app.models.user import Role, User
from app.schemas.project_file import ProjectFileListItem, ProjectFileRead, ProjectFileUpdate
from app.services import storage

router = APIRouter(prefix="/projects", tags=["project-files"])
logger = logging.getLogger(__name__)

# Extension -> declared content-types accepted for that extension. An allowlist,
# not a blocklist, so executables (.exe, .sh, .bat, .js, .msi, ...) are rejected
# implicitly by simply never appearing here.
ALLOWED_EXTENSIONS: dict[str, set[str]] = {
    ".pdf": {"application/pdf"},
    ".doc": {"application/msword"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".txt": {"text/plain"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
    ".csv": {"text/csv", "application/vnd.ms-excel"},
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    ".pptx": {"application/vnd.openxmlformats-officedocument.presentationml.presentation"},
}


def _project_access(db: Session, project_id: int, current_user: User) -> Project:
    """Object-level access check shared by every file endpoint.

    Project must exist and be active; CLIENT must own it. Returns 404 (not 403)
    for any failure, matching the convention used for milestones and projects.
    """
    project = project_crud.get_by_id(db, project_id)
    if not project or not project.is_active:
        raise HTTPException(status_code=404, detail="Project not found or is inactive")
    if current_user.role == Role.CLIENT and project.client_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found or is inactive")
    return project


def _validate_upload(file: UploadFile) -> str:
    """Validate filename extension and declared content-type. Returns the lowercase extension."""
    extension = Path(file.filename or "").suffix.lower()
    allowed_content_types = ALLOWED_EXTENSIONS.get(extension)
    if not allowed_content_types:
        raise HTTPException(
            status_code=415, detail=f"File type '{extension or 'unknown'}' is not allowed"
        )
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=415,
            detail=f"Declared content-type '{file.content_type}' is not allowed for '{extension}' files",
        )
    return extension


@router.post(
    "/{project_id}/files",
    response_model=ProjectFileRead,
    status_code=201,
    summary="Upload a project file",
)
def upload_file(
    project_id: int,
    db: DbDep,
    current_user: ActiveUser,
    file: UploadFile = File(...),
    category: FileCategory = Form(FileCategory.DOCUMENT),
    description: str | None = Form(None),
):
    """Upload a file to a project. CLIENT may only upload to their own active project."""
    _project_access(db, project_id, current_user)
    extension = _validate_upload(file)

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    try:
        stored_filename, storage_path, file_size = storage.save_file(
            file.file, project_id, extension, max_size_bytes
        )
    except storage.FileTooLargeError:
        raise HTTPException(
            status_code=413, detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit"
        )

    project_file = file_crud.create(
        db,
        project_id=project_id,
        uploaded_by=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        content_type=file.content_type,
        file_size=file_size,
        category=category,
        description=description,
    )
    logger.info(
        "user %s uploaded file %s to project %s", current_user.id, project_file.id, project_id
    )
    return project_file


@router.get(
    "/{project_id}/files",
    response_model=list[ProjectFileListItem],
    summary="List project files",
)
def list_files(
    project_id: int,
    db: DbDep,
    current_user: ActiveUser,
    category: FileCategory | None = None,
    include_inactive: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    _project_access(db, project_id, current_user)

    # CLIENT cannot see soft-deleted files
    if current_user.role == Role.CLIENT:
        include_inactive = False

    return file_crud.list_files(
        db,
        project_id,
        limit=limit,
        offset=offset,
        category=category,
        include_inactive=include_inactive,
    )


@router.get(
    "/{project_id}/files/{file_id}",
    response_model=ProjectFileRead,
    summary="Get file metadata",
)
def get_file(project_id: int, file_id: int, db: DbDep, current_user: ActiveUser):
    _project_access(db, project_id, current_user)

    file = file_crud.get_by_id_for_project(db, file_id, project_id)
    if not file or not file.is_active:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.get(
    "/{project_id}/files/{file_id}/download",
    summary="Download a project file",
)
def download_file(project_id: int, file_id: int, db: DbDep, current_user: ActiveUser):
    _project_access(db, project_id, current_user)

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


@router.patch(
    "/{project_id}/files/{file_id}",
    response_model=ProjectFileRead,
    summary="Update file metadata",
)
def update_file(
    project_id: int,
    file_id: int,
    data: ProjectFileUpdate,
    db: DbDep,
    current_user: ActiveUser,
):
    """Update file metadata (category, description). Never touches the stored binary.

    ADMIN/STAFF may update any file's metadata; CLIENT only their own uploads.
    """
    _project_access(db, project_id, current_user)

    file = file_crud.get_by_id_for_project(db, file_id, project_id)
    if not file or not file.is_active:
        raise HTTPException(status_code=404, detail="File not found")

    if current_user.role == Role.CLIENT and file.uploaded_by != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")

    updated = file_crud.update_metadata(db, file, data)
    logger.info(
        "user %s updated file %s metadata for project %s", current_user.id, file_id, project_id
    )
    return updated


@router.delete(
    "/{project_id}/files/{file_id}",
    response_model=ProjectFileRead,
    summary="Soft-delete a project file",
)
def delete_file(project_id: int, file_id: int, db: DbDep, current_user: ActiveUser):
    """Soft-delete a file. ADMIN can delete any file; STAFF cannot delete (existing
    convention, matching milestones); CLIENT may delete only files they uploaded
    themselves, within their own project."""
    if current_user.role == Role.STAFF:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    _project_access(db, project_id, current_user)

    file = file_crud.get_by_id_for_project(db, file_id, project_id)
    if not file or not file.is_active:
        raise HTTPException(status_code=404, detail="File not found")

    if current_user.role == Role.CLIENT and file.uploaded_by != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")

    updated = file_crud.deactivate(db, file)
    logger.info("user %s deleted file %s for project %s", current_user.id, file_id, project_id)
    return updated
