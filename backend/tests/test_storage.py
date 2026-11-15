
import asyncio
import hashlib
from io import BytesIO

from starlette.datastructures import UploadFile

from app.services.storage_service import (
    store_file,
    get_file_path,
    verify_file,
    delete_stored_file
)


async def main():

    content = b"PiCloud storage engine test"

    upload = UploadFile(
        filename="test.txt",
        file=BytesIO(content),
        headers=None
    )

    result = await store_file(upload)

    print("\nUpload result:")
    print(result)

    # Verify physical file exists
    path = get_file_path(result["storage_key"])

    assert path.is_file()
    print("\n[PASS] File physically stored")

    # Verify file contents
    assert path.read_bytes() == content
    print("[PASS] File contents match")

    # Verify checksum
    expected = hashlib.sha256(content).hexdigest()

    assert result["checksum"] == expected
    assert verify_file(
        result["storage_key"],
        expected
    )

    print("[PASS] SHA-256 verification successful")

    # Test deletion
    delete_stored_file(result["storage_key"])

    assert not path.exists()
    print("[PASS] File deletion successful")

    print("\nAll storage tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
