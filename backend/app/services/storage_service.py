
import hashlib
import os
import tempfile
import uuid

from pathlib import Path
from fastapi import UploadFile

from app.core.config import STORAGE_PATH, MAX_UPLOAD_SIZE


# Storage directories
STORAGE_ROOT = Path(STORAGE_PATH).resolve()

OBJECTS_DIR = STORAGE_ROOT / "objects"
TEMP_DIR = STORAGE_ROOT / "temp"


def initialize_storage():
    """Create storage directories if they do not exist."""

    OBJECTS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


async def store_file(upload: UploadFile):
    """
    Stream an uploaded file into temporary storage,
    calculate SHA-256, and atomically move it
    into permanent object storage.
    """

    initialize_storage()

    temp_path = None

    try:
        # Generate a unique storage identifier
        storage_id = uuid.uuid4().hex

        # Preserve the original filename as metadata only
        original_name = Path(
            (upload.filename or "").replace("\\", "/")
        ).name

        if not original_name or original_name in (".", ".."):
            raise ValueError("Invalid filename")

        file_size = 0
        sha256 = hashlib.sha256()

        # Create temporary file on the same filesystem
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=TEMP_DIR,
            prefix=".upload-",
            delete=False
        ) as temp_file:

            temp_path = Path(temp_file.name)

            while True:

                chunk = await upload.read(1024 * 1024)

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_UPLOAD_SIZE:
                    raise ValueError(
                        "File exceeds maximum upload size"
                    )

                sha256.update(chunk)

                temp_file.write(chunk)

            temp_file.flush()
            os.fsync(temp_file.fileno())

        # Generate a two-level directory structure
        storage_key = (
            f"{storage_id[:2]}/"
            f"{storage_id[2:4]}/"
            f"{storage_id}"
        )

        destination = OBJECTS_DIR / storage_key

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Atomic move from temporary to permanent storage
        os.replace(temp_path, destination)

        temp_path = None

        return {
            "name": original_name,
            "storage_key": storage_key,
            "size": file_size,
            "checksum": sha256.hexdigest(),
            "mime_type": upload.content_type
        }

    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

        raise

    finally:
        await upload.close()


def get_file_path(storage_key: str) -> Path:
    """Resolve a storage key safely within object storage."""

    root = OBJECTS_DIR.resolve()
    candidate = (root / storage_key).resolve()

    if not candidate.is_relative_to(root):
        raise ValueError("Invalid storage key")

    return candidate


def delete_stored_file(storage_key: str):
    """Delete a physically stored object."""

    file_path = get_file_path(storage_key)

    if file_path.is_file():
        file_path.unlink()


def verify_file(storage_key: str, expected_checksum: str) -> bool:
    """Verify the SHA-256 checksum of a stored object."""

    file_path = get_file_path(storage_key)

    if not file_path.is_file():
        return False

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest() == expected_checksum
