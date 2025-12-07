# backend/app/agents/clinical_trials_agent.py
import httpx
import json
import os
from .worker_base import WorkerAgent

CT_V2 = "https://clinicaltrials.gov/api/v2/studies"
ALLORIGINS = "https://api.allorigins.win/raw?url="
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MOCK_FILE = os.path.join(DATA_DIR, "mock_clinical_trials.json")

def load_mock(term: str):
    try:
        with open(MOCK_FILE, "r", encoding="utf-8") as f:
            j = json.load(f)
        return j.get(term.lower(), j.get("default", {}))
    except Exception:
        return {"trials": [], "notes": "mock load failed"}

class ClinicalTrialsAgent(WorkerAgent):
    async def _get_json(self, client: httpx.AsyncClient, url: str, params=None):
        r = await client.get(url, params=params, timeout=30.0)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return json.loads(r.text)

    def _parse_v2(self, studies):
        parsed = []
        for s in studies:
            try:
                proto = s.get("protocolSection", {})
                idm = proto.get("identificationModule", {})
                design = proto.get("designModule", {})
                status_m = proto.get("statusModule", {})
                conds = proto.get("conditionsModule", {})
                sponsor_m = proto.get("sponsorCollaboratorsModule", {})
                parsed.append({
                    "nct_id": idm.get("nctId"),
                    "title": idm.get("briefTitle"),
                    "phase": design.get("phases", []),
                    "status": status_m.get("overallStatus"),
                    "conditions": conds.get("conditions", []),
                    "sponsor": sponsor_m.get("leadSponsor", {}).get("name")
                })
            except Exception:
                continue
        return parsed

    async def run(self, payload: dict) -> dict:
        term = (payload.get("molecule") or payload.get("disease") or "").strip()
        if not term:
            return {"status": "error", "data": [], "notes": "No molecule provided"}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Referer": "https://clinicaltrials.gov/",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # 1) Try direct v2 API with proper headers
        try:
            async with httpx.AsyncClient(headers=headers) as client:
                body = await self._get_json(client, CT_V2, params={"query.term": term, "pageSize": "20"})
            studies = body.get("studies", [])
            parsed = self._parse_v2(studies)
            return {"status": "ok", "n_found": len(parsed), "data": parsed, "notes": "Fetched from clinicaltrials.gov v2"}
        except Exception as e_direct:
            direct_err = repr(e_direct)

        # 2) Try AllOrigins proxy (may be flaky)
        try:
            proxied = ALLORIGINS + CT_V2 + f"?query.term={term}&pageSize=20"
            async with httpx.AsyncClient(headers=headers) as client:
                body = await self._get_json(client, proxied, params=None)
            studies = body.get("studies", []) if isinstance(body, dict) else []
            parsed = self._parse_v2(studies)
            if parsed:
                return {"status": "ok", "n_found": len(parsed), "data": parsed, "notes": "Fetched via AllOrigins proxy"}
        except Exception as e_proxy:
            proxy_err = repr(e_proxy)

        # 3) Fallback to local mock (guaranteed)
        mock = load_mock(term)
        trials = mock.get("trials", []) if isinstance(mock, dict) else []
        notes = f"Direct error: {direct_err} | Proxy error: {proxy_err} | returned mock"
        return {"status": "fallback", "n_found": len(trials), "data": trials, "notes": notes}
