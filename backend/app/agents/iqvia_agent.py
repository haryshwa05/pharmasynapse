import httpx
from .worker_base import WorkerAgent

MOCK_BASE = "http://localhost:8000/mock/iqvia"

class IQVIAAgent(WorkerAgent):
    async def run(self, payload: dict) -> dict:
        therapy = payload.get("molecule", "").lower()
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"{MOCK_BASE}/{therapy}")
                data = r.json()
            except Exception as e:
                return {"status": "error", "data": {}, "notes": f"iqvia mock fetch error: {e}"}
        return {
            "status": "ok",
            "data": data,
            "notes": f"Mock IQVIA data for '{therapy}'"
        }
