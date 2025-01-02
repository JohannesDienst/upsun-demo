from fastapi import FastAPI, File, UploadFile, Form
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/convert-file/")
async def convert(
    filename: Annotated[str, Form()],
    extension: Annotated[str, Form()],
    file: Annotated[UploadFile, File()]
):
    # Read the uploaded file's content
    content = await file.read()

    # Log or process the uploaded data
    return {
        "filename": filename,
        "extension": extension,
        "file_content_size": len(content),
        "uploaded_filename": file.filename,
        "content_type": file.content_type,
    }
