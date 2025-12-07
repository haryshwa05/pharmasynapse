import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

DOCS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "internal_docs"))

router = APIRouter()

os.makedirs(DOCS_DIR, exist_ok=True)


@router.post("/internal/upload")
async def upload_internal_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are allowed.")
    save_path = os.path.join(DOCS_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"ok": True, "filename": file.filename, "path": f"/internal/docs/{file.filename}"}


@router.get("/internal/docs/{filename}")
async def get_internal_pdf(filename: str):
    safe_path = os.path.join(DOCS_DIR, filename)
    if not os.path.isfile(safe_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(safe_path, media_type="application/pdf", filename=filename)

