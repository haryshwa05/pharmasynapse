import os
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any

from app.agents.report_agent import ReportAgent
from app.report.report_generator import OUT_DIR, ReportGenerator

router = APIRouter()
agent = ReportAgent()
report_generator = ReportGenerator()


class ReportRequest(BaseModel):
    molecule: str
    disease: str | None = None
    region: str | None = None


@router.post("/report/generate")
def generate_report(req: ReportRequest):
    """Generate legacy molecule analysis report."""
    if not req.molecule:
        raise HTTPException(status_code=400, detail="molecule is required")
    result = agent.run(req.model_dump())
    return {"ok": True, **result}


@router.post("/report/generate-comprehensive")
async def generate_comprehensive_report(workflow_result: Dict[str, Any] = Body(...)):
    """
    Generate comprehensive detailed PDF report from workflow results.

    This generates a full detailed report with all agent outputs, visualizations,
    and strategic insights instead of the 5-slide format.
    """
    try:
        # Generate comprehensive detailed report
        report_path = report_generator.generate_comprehensive_report(workflow_result)

        # Extract filename
        filename = os.path.basename(report_path)

        return {
            "ok": True,
            "report_path": report_path,
            "filename": filename,
            "download_url": f"/api/reports/{filename}",
            "message": "Comprehensive detailed report generated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comprehensive report: {str(e)}"
        )


@router.get("/reports/{filename}")
def download_report(filename: str):
    """Download any generated report by filename."""
    safe_path = os.path.join(OUT_DIR, filename)
    if not os.path.isfile(safe_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(safe_path, media_type="application/pdf", filename=filename)

