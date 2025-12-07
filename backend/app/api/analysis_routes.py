# backend/app/api/analysis_routes.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.agents.master_agent import MasterAgent

router = APIRouter()
master_agent = MasterAgent()


class MoleculeAnalysisRequest(BaseModel):
    molecule: str
    disease: Optional[str] = None
    region: Optional[str] = None


@router.post("/analyze-molecule")
def analyze_molecule(req: MoleculeAnalysisRequest):
    """
    High-level endpoint: given a molecule (+ optional disease/region),
    returns IQVIA + Patent (and later Trials/Web/etc.) insights.
    """
    result = master_agent.analyze_molecule(
        molecule=req.molecule,
        disease=req.disease,
        region=req.region
    )
    return result
