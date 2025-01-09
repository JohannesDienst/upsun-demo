from enum import Enum
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Header, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.security import APIKeyHeader
from typing import Annotated
import base64

app = FastAPI()

from ..database.database_upsun import validate_api_key
header_scheme = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key: str = Header(None)):
    api_key_valid = validate_api_key(api_key)
    if not api_key_valid:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/")
async def root():
    return {"message": "Hello and welcome to Image Converter"}

class TargetFormat(str, Enum):
    """Enum representing supported target formats."""
    WEBP = "webp"

from PIL import Image
from io import BytesIO
def convert_to_target_format(content, target_format):
    # Convert the content to the target format
    if target_format == TargetFormat.WEBP:
        image = Image.open(BytesIO(content))
        output_buffer = BytesIO()
        image.save(output_buffer, 'webp', optimize=True, quality=60)
        return output_buffer.getvalue()

@app.post("/convert-file-to-base64/")
async def convertToBase64(
    file: Annotated[UploadFile, File()],
    target_format: TargetFormat,
    key: Annotated[str, Depends(check_api_key)]
):
    # Read the uploaded file's content
    content = await file.read()

    if target_format == TargetFormat.WEBP:
       converted_content = convert_to_target_format(content, target_format)
       file_extension="webp"
       pass

    converted_content_base64 = base64.b64encode(converted_content).decode('utf-8')

    # Log or process the uploaded data
    return JSONResponse(
        content={
           "filename": file.filename,
           "content_type": file.content_type,
           "target_format": file_extension,
           "converted_file": converted_content_base64,
       },
       status_code=200,
    )

@app.post("/convert-file-to-file/")
async def convertToFile(
    file: Annotated[UploadFile, File()],
    target_format: TargetFormat,
    key: Annotated[str, Depends(check_api_key)]
):
    # Read the uploaded file's content
    content = await file.read()

    if target_format == TargetFormat.WEBP:
       converted_content = convert_to_target_format(content, target_format)
       file_extension="webp"
       pass

    #return Response(content=image_bytes, media_type="image/png")
    # Log or process the uploaded data
    return Response(
        content=converted_content,
        media_type="image/{target_format}".format(target_format=file_extension)
    )

from fastapi import FastAPI, HTTPException
from datetime import datetime

# Import the functions for managing API keys
from ..database.database_upsun import Base, engine, Session, APIKey
from ..database.database_upsun import get_api_keys, add_api_key, delete_api_key

# Create an endpoint to get API keys for a specific user
@app.get('/api_keys/{username}')
def get_user_api_keys(
    username: str,
    key: str):
    api_key_valid = validate_api_key(key)
    if not api_key_valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    api_keys = get_api_keys(username, key)
    if api_keys is None:
        raise HTTPException(status_code=401, detail=f'API Key is correct but belongs to another user.')
    if not api_keys:
        raise HTTPException(status_code=404, detail=f'No API keys found for user: {username}')
    return api_keys

class ApiKeyRequest(BaseModel):
    expiration_date: datetime

# Create an endpoint to add a new API key for a user
@app.post('/add_api_key')
def add_user_api_key(
    request: ApiKeyRequest,
    key: str):
    api_key_valid = validate_api_key(key)
    if not api_key_valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return_value = add_api_key(key, request.expiration_date)
    if return_value is None:
        raise HTTPException(status_code=500, detail='The API Key is valid but somehow there is no username. Please contact support.')
    return JSONResponse(
        content={
            "key": return_value
        },
        status_code=200,
    )

class ApiKeyDeleteRequest(BaseModel):
    key_id: str
    api_key: str
@app.delete('/delete_api_key')
def delete_user_api_key(request: ApiKeyDeleteRequest):
    api_key_valid = validate_api_key(request.api_key)
    if not api_key_valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    success = delete_api_key(request.key_id, request.api_key)
    if success:
        return {'message': f'API key {request.key_id} deleted successfully.'}
    else:
        raise HTTPException(status_code=404, detail=f'API key {request.key_id} not found.')
