import os
import shutil
from tempfile import TemporaryDirectory

from fastapi import HTTPException, UploadFile
from fastapi.routing import APIRouter

DATA_ROOT = "/tmp/vidi18n/"

router = APIRouter()


def validate_path(path: str) -> str:
    """
    Gets the path to the file, or raises an exception if the path is invalid
    """
    full_path = os.path.join(DATA_ROOT, path)
    real_path = os.path.realpath(full_path)

    if not real_path.startswith(DATA_ROOT):
        raise HTTPException(status_code=403, detail="Nice try, chummer.")

    return real_path


@router.put("/{param:path}", name="path-convertor")
async def upload_file(path: str, upload: UploadFile) -> None:
    """
    Save the file to disk
    """
    path = validate_path(path)

    with TemporaryDirectory() as tmpdir:
        tmp_path = os.path.join(tmpdir, os.path.basename(path))
        with open(tmp_path, "wb") as f:
            f.write(await upload.read())
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.move(tmp_path, path)


@router.get("/{param:path}", name="path-convertor")
async def get_file(path: str) -> bytes:
    path = validate_path(path)

    with open(path, "rb") as f:
        return f.read()
