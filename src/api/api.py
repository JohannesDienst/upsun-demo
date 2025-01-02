from enum import Enum
from fastapi import FastAPI, File, UploadFile, Header, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.security import APIKeyHeader
from typing import Annotated
import base64

app = FastAPI()

header_scheme = APIKeyHeader(name="X-API-Key")

def check_api_key(api_key: str = Header(None)):
    # In a real scenario, you would validate the API key against a database or a secure storage
    valid_api_key = "12345"
    if api_key != valid_api_key:
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