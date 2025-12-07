import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agents.report_agent import ReportAgent
from app.report.report_generator import OUT_DIR

router = APIRouter()
agent = ReportAgent()


class ReportRequest(BaseModel):
    molecule: str
    disease: str | None = None
    region: str | None = None


@router.post("/report/generate")
def generate_report(req: ReportRequest):
    if not req.molecule:
        raise HTTPException(status_code=400, detail="molecule is required")
    result = agent.run(req.model_dump())
    return {"ok": True, **result}


@router.get("/reports/{filename}")
def download_report(filename: str):
    safe_path = os.path.join(OUT_DIR, filename)
    if not os.path.isfile(safe_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(safe_path, media_type="application/pdf", filename=filename)

