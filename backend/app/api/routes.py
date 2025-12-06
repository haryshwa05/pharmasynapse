# backend/app/api/routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.master_agent import MasterAgent

router = APIRouter()

class QueryRequest(BaseModel):
    prompt: str
    molecule: str

@router.post("/run-research")
async def run_research(payload: QueryRequest):
    master = MasterAgent()
    result = await master.handle_query(payload.dict())
    return {"ok": True, "result": result}
