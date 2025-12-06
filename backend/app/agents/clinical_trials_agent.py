# backend/app/agents/clinical_trials_agent.py
import httpx
from .worker_base import WorkerAgent

# Base URL for our local mock clinical endpoints
MOCK_BASE = "http://localhost:8000/mock/clinical"

class ClinicalTrialsAgent(WorkerAgent):
    async def run(self, payload: dict) -> dict:
        """
        Query the mock clinical endpoint for the given molecule/disease.
        Returns a dict with status, data, notes.
        """
        term = payload.get("molecule", "").lower()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{MOCK_BASE}/{term}")
                data = resp.json()
            except Exception as e:
                return {"status": "error", "data": {}, "notes": f"clinical mock fetch error: {e}"}
        return {
            "status": "ok",
            "data": data,
            "notes": f"Mock clinical data for '{term}'"
        }
