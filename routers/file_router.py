import io
import uuid
import os
from pathlib import Path
from PIL import Image
from fastapi import APIRouter, status, Depends, File, HTTPException, UploadFile
from fastapi_jwt_auth import AuthJWT

from helpers.authentication import validate_token
from helpers.config import BASE_DIR

UPLOAD_DIRS = os.path.join(BASE_DIR , "uploads")

file_router = APIRouter(
    prefix="/file",
    tags=["file"]
)

@file_router.post('/upload-file')
@validate_token
async def upload_file(Authorize: AuthJWT=Depends(), file: UploadFile = File(...)):
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format')
    fname = Path(file.filename)
    fext = fname.suffix
    dest = UPLOAD_DIRS / f"{uuid.uuid1()}{fext}"
    img.save(dest)
    return {"message": "Upload file succeed"}