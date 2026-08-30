from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project_file import FileCategory


class ProjectFileUpdate(BaseModel):
    category: FileCategory | None = None
    description: str | None = Field(default=None, max_length=5000)


class ProjectFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    uploaded_by: int
    original_filename: str
    content_type: str
    file_size: int
    category: FileCategory
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProjectFileListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    uploaded_by: int
    original_filename: str
    content_type: str
    file_size: int
    category: FileCategory
    description: str | None
    is_active: bool
    created_at: datetime
