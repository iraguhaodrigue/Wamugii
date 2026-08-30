import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


class StorageError(Exception):
    """Base error for storage operations."""


class FileTooLargeError(StorageError):
    """Raised when an uploaded stream exceeds the configured size limit."""


def _upload_root() -> Path:
    root = Path(settings.UPLOAD_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_within_root(relative_path: str) -> Path:
    """Resolve `relative_path` against the upload root, rejecting any path that escapes it."""
    root = _upload_root()
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise StorageError(f"Path '{relative_path}' escapes the upload root")
    return candidate


def save_file(
    fileobj: BinaryIO, project_id: int, extension: str, max_size_bytes: int
) -> tuple[str, str, int]:
    """
    Stream `fileobj` to uploads/projects/{project_id}/{generated_uuid}{extension}.

    Returns (stored_filename, storage_path, file_size); storage_path is relative
    to UPLOAD_DIR, suitable for persisting in the database. Raises
    FileTooLargeError if the stream exceeds max_size_bytes, removing the
    partial file first.
    """
    project_dir = _resolve_within_root(f"projects/{project_id}")
    project_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    storage_path = f"projects/{project_id}/{stored_filename}"
    dest = project_dir / stored_filename

    size = 0
    try:
        with open(dest, "wb") as out:
            while True:
                chunk = fileobj.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_size_bytes:
                    raise FileTooLargeError(f"File exceeds the {max_size_bytes} byte limit")
                out.write(chunk)
    except Exception:
        dest.unlink(missing_ok=True)
        raise

    return stored_filename, storage_path, size


def get_file(storage_path: str) -> Path:
    """Resolve a stored relative path to an absolute filesystem path."""
    return _resolve_within_root(storage_path)


def delete_file(storage_path: str) -> None:
    """Best-effort removal of the physical file. Never raises for a missing file."""
    try:
        path = _resolve_within_root(storage_path)
    except StorageError:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
