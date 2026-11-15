from pathlib import Path
from fastapi.responses import FileResponse as DownloadResponse

from app.services.storage_service import get_file_path
from app.services.scanner import scan_storage

from app.schemas.file_schema import (
    FileResponse,
    FileListResponse
)

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import StoredFile, Folder, User
from app.schemas.file_schema import FileResponse
from app.services.storage_service import (
    store_file,
    delete_stored_file
)


router = APIRouter(
    prefix="/api/files",
    tags=["Files"]
)

# Temporary development identity.
# Replace with authenticated user identity later.
DEV_USER_ID = 1


@router.post(
    "/upload",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file: UploadFile = File(...),
    folder_id: int | None = Form(None),
    db: Session = Depends(get_db)
):

    # Verify development user exists
    user = db.query(User).filter(
        User.id == DEV_USER_ID
    ).first()

    if not user:
        await file.close()
        raise HTTPException(
            status_code=500,
            detail="Development user not configured"
        )

    # Verify destination folder belongs to this user
    if folder_id is not None:
        folder = db.query(Folder).filter(
            Folder.id == folder_id,
            Folder.owner_id == DEV_USER_ID
        ).first()

        if not folder:
            await file.close()
            raise HTTPException(
                status_code=404,
                detail="Folder not found"
            )

    stored = None

    try:
        # Store the physical file
        stored = await store_file(file)

        # Create database metadata
        db_file = StoredFile(
            name=stored["name"],
            storage_key=stored["storage_key"],
            size=stored["size"],
            mime_type=stored["mime_type"],
            checksum=stored["checksum"],
            folder_id=folder_id,
            owner_id=DEV_USER_ID
        )

        db.add(db_file)

        db.commit()
        db.refresh(db_file)

        return db_file

    except ValueError as error:
        db.rollback()

        if stored:
            delete_stored_file(stored["storage_key"])

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        db.rollback()

        if stored:
            try:
                delete_stored_file(stored["storage_key"])
            except OSError:
                pass

        raise HTTPException(
            status_code=500,
            detail="File upload failed"
        )

@router.get("/", response_model=FileListResponse)
def list_files(
    folder_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Verify development user
    user = db.query(User).filter(
        User.id == DEV_USER_ID
    ).first()

    if not user:
        raise HTTPException(
            status_code=500,
            detail="Development user not configured"
        )

    query = db.query(StoredFile).filter(
        StoredFile.owner_id == DEV_USER_ID
    )

    # Root directory or specific folder
    if folder_id is None:
        query = query.filter(
            StoredFile.folder_id.is_(None)
        )
    else:
        folder = db.query(Folder).filter(
            Folder.id == folder_id,
            Folder.owner_id == DEV_USER_ID
        ).first()

        if not folder:
            raise HTTPException(
                status_code=404,
                detail="Folder not found"
            )

        query = query.filter(
            StoredFile.folder_id == folder_id
        )

    files = query.order_by(
        StoredFile.created_at.desc()
    ).all()

    return {
        "total": len(files),
        "files": files
    }
@router.post("/scan")
def scan_files(db: Session = Depends(get_db)):

    try:
        result = scan_storage(db)

        return {
            "status": "success",
            "message": "Storage scan completed",
            **result
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Storage scan failed"
        )

@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    db_file = db.query(StoredFile).filter(
        StoredFile.id == file_id,
        StoredFile.owner_id == DEV_USER_ID
    ).first()

    if not db_file:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    try:
        file_path = get_file_path(db_file.storage_key)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid storage location"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found"
        )

    return DownloadResponse(
        path=file_path,
        filename=db_file.name,
        media_type=db_file.mime_type or "application/octet-stream"
    )
