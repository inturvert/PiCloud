from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    id: int
    name: str
    size: int
    mime_type: str | None
    checksum: str
    folder_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    total: int
    files: list[FileResponse]
