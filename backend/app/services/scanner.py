
import hashlib
from pathlib import Path
import mimetypes

from sqlalchemy.orm import Session

from app.core.config import STORAGE_PATH
from app.database.models import StoredFile, User


OBJECTS_DIR = (Path(STORAGE_PATH) / "objects").resolve()

# Temporary development user
DEV_USER_ID = 1


def calculate_checksum(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_storage(db: Session):

    user = db.query(User).filter(
        User.id == DEV_USER_ID
    ).first()

    if not user:
        raise RuntimeError("Development user not found")

    discovered = 0
    skipped = 0

    OBJECTS_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in OBJECTS_DIR.rglob("*"):

        if not file_path.is_file():
            continue

        # Ignore symbolic links
        if file_path.is_symlink():
            skipped += 1
            continue

        storage_key = file_path.relative_to(
            OBJECTS_DIR
        ).as_posix()

        existing = db.query(StoredFile).filter(
            StoredFile.storage_key == storage_key
        ).first()

        if existing:
            skipped += 1
            continue

        checksum = calculate_checksum(file_path)

        mime_type, _ = mimetypes.guess_type(file_path.name)

        db_file = StoredFile(
            name=file_path.name,
            storage_key=storage_key,
            size=file_path.stat().st_size,
            mime_type=mime_type or "application/octet-stream",
            checksum=checksum,
            folder_id=None,
            owner_id=DEV_USER_ID
        )

        db.add(db_file)
        discovered += 1

    db.commit()

    return {
        "discovered": discovered,
        "skipped": skipped
    }
