import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

import httpx

from .worker_base import WorkerBase

# ---------- CONFIG ----------

# PatentsView PatentSearch API (US patents)
PATENTSVIEW_BASE_URL = "https://search.patentsview.org/api/v1/patent/"
PATENTSVIEW_API_KEY = os.getenv("PATENTSVIEW_API_KEY")

# Local mock data fallback
MOCK_DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "mock_patents.json"
)


class PatentLandscapeAgent(WorkerBase):
    """
    Worker Agent that provides a patent landscape for a molecule.
    First tries live PatentsView PatentSearch API, then falls back to mock JSON.
    """

    def __init__(self, data_path: str = MOCK_DATA_FILE):
        self.data_path = data_path
        self._mock_cache: Optional[Dict[str, Any]] = None

    # ------------ PUBLIC ENTRYPOINT ------------

    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        query example:
        {
          "molecule": "metformin",
          "indication": "NAFLD"   # optional
        }
        """
        molecule = query.get("molecule")
        indication = query.get("indication")

        if not molecule:
            raise ValueError("PatentLandscapeAgent requires 'molecule' in query")

        # 1) Try live PatentsView API if we have a key
        if PATENTSVIEW_API_KEY:
            try:
                live_result = self._run_live(molecule=molecule, indication=indication)
                if live_result is not None and live_result.get("patents"):
                    return live_result
            except Exception as e:
                # In hackathon mode, just fall back silently
                print(f"[PatentLandscapeAgent] Live API failed, falling back to mock. Error: {e}")

        # 2) Fallback to mock JSON
        return self._run_mock(molecule=molecule, indication=indication)

    # ------------ LIVE API PATH ------------

    def _run_live(self, molecule: str, indication: Optional[str]) -> Dict[str, Any]:
        """
        Query PatentsView PatentSearch API for patents whose TITLE mentions the molecule.
        Optionally, you could also search abstract/claims by adjusting the query.
        """
        patents = self._fetch_patents_from_patentsview(molecule)

        if not patents:
            # no live data for this molecule
            return {
                "molecule": molecule,
                "patents": [],
                "overview": {
                    "total": 0,
                    "active_count": 0,
                    "expired_count": 0,
                    "pending_count": 0,
                    "earliest_active_expiry": None,
                    "has_any_freedom_to_operate": True,
                    "as_of_date": datetime.today().date().isoformat(),
                },
                "available": False,
                "summary": f"No live patent data found via PatentsView for {molecule}."
            }

        # map PatentsView patents → your internal structure
        mapped_patents = [self._map_patent_record(p) for p in patents]

        overview = self._build_overview_from_live(mapped_patents)
        summary = self._build_summary(
            molecule=molecule,
            total=overview["total"],
            active=overview["active_count"],
            expired=overview["expired_count"],
            pending=overview["pending_count"],
            earliest_active_expiry=overview["earliest_active_expiry"],
            source="live PatentsView API"
        )

        return {
            "molecule": molecule,
            "patents": mapped_patents,
            "overview": overview,
            "available": True,
            "summary": summary,
        }

    def _fetch_patents_from_patentsview(self, molecule: str) -> List[Dict[str, Any]]:
        """
        Calls PatentsView PatentSearch API.
        Simple strategy: search in patent_title for the molecule string.
        """
        if not PATENTSVIEW_API_KEY:
            raise RuntimeError("PATENTSVIEW_API_KEY is not set")

        # Build query parameters according to PatentSearch API
        # q = {"_text_any": {"patent_title": "metformin"}}
        q_obj = {"_text_any": {"patent_title": molecule}}

        # fields we care about for demo
        f_obj = [
            "patent_id",
            "patent_title",
            "patent_date",
            "patent_type",
            "assignees.assignee_organization"
        ]

        o_obj = {
            "size": 20  # limit to first 20 for demo
        }

        params = {
            "q": json.dumps(q_obj),
            "f": json.dumps(f_obj),
            "o": json.dumps(o_obj),
        }

        headers = {
            "X-Api-Key": PATENTSVIEW_API_KEY
        }

        with httpx.Client(timeout=15) as client:
            resp = client.get(PATENTSVIEW_BASE_URL, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        if data.get("error"):
            # API-level error; treat as no data
            return []

        # According to docs, response key is endpoint name, e.g. "patents"
        patents = data.get("patents", [])
        return patents

    def _map_patent_record(self, p: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a PatentsView patent record into your internal patent dict.
        """
        patent_id = p.get("patent_id")
        title = p.get("patent_title")
        date = p.get("patent_date")
        ptype = p.get("patent_type")

        # assignees is usually a list
        assignees = p.get("assignees") or []
        if assignees:
            assignee_name = assignees[0].get("assignee_organization")
        else:
            assignee_name = None

        # PatentsView doesn't give us legal status directly (active/expired/pending),
        # so for demo we make a simple heuristic:
        status = self._infer_status_from_date(date)

        return {
            "patent_number": patent_id,
            "title": title,
            "assignee": assignee_name,
            "jurisdiction": "US",
            "status": status,           # "active"/"expired"/"pending" (heuristic)
            "expiry_date": None,        # unknown from this API; keep None for now
            "family_id": None,
            "focus": None,
            "fto_risk": "unknown",
        }

    def _infer_status_from_date(self, patent_date: Optional[str]) -> str:
        """
        Very rough heuristic for demo:
        - if grant date older than ~20 years → expired
        - else → active
        """
        if not patent_date:
            return "unknown"

        try:
            grant_year = int(patent_date.split("-")[0])
        except Exception:
            return "unknown"

        current_year = datetime.today().year
        if current_year - grant_year > 20:
            return "expired"
        else:
            return "active"

    def _build_overview_from_live(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(patents)
        active = sum(1 for p in patents if p.get("status") == "active")
        expired = sum(1 for p in patents if p.get("status") == "expired")
        pending = sum(1 for p in patents if p.get("status") == "pending")

        # no expiry dates from API, keep None
        earliest_expiry = None

        has_fto = expired > 0 or total == 0

        return {
            "total": total,
            "active_count": active,
            "expired_count": expired,
            "pending_count": pending,
            "earliest_active_expiry": earliest_expiry,
            "has_any_freedom_to_operate": has_fto,
            "as_of_date": datetime.today().date().isoformat(),
        }

    # ------------ MOCK PATH (FALLBACK) ------------

    def _load_mock_data(self) -> Dict[str, Any]:
        if self._mock_cache is None:
            with open(self.data_path, "r") as f:
                self._mock_cache = json.load(f)
        return self._mock_cache

    def _get_mock_entry(self, molecule: str) -> Optional[Dict[str, Any]]:
        data = self._load_mock_data()
        return data.get(molecule.lower())

    def _run_mock(self, molecule: str, indication: Optional[str]) -> Dict[str, Any]:
        entry = self._get_mock_entry(molecule)
        if not entry:
            return {
                "molecule": molecule,
                "patents": [],
                "overview": {
                    "total": 0,
                    "active_count": 0,
                    "expired_count": 0,
                    "pending_count": 0,
                    "earliest_active_expiry": None,
                    "has_any_freedom_to_operate": True,
                    "as_of_date": datetime.today().date().isoformat(),
                },
                "available": False,
                "summary": f"No mock patent data found for {molecule}."
            }

        patents = entry.get("patents", [])
        overview = entry.get("overview")
        if not overview:
            overview = self._build_overview_from_mock(patents)

        summary = self._build_summary(
            molecule=entry.get("molecule", molecule),
            total=overview["total"],
            active=overview["active_count"],
            expired=overview["expired_count"],
            pending=overview["pending_count"],
            earliest_active_expiry=overview["earliest_active_expiry"],
            source="mock data"
        )

        status_table = entry.get("status_table", [])
        filing_heatmap = entry.get("filing_heatmap", {})

        return {
            "molecule": entry.get("molecule", molecule),
            "patents": patents,
            "overview": overview,
            "status_table": status_table,
            "filing_heatmap": filing_heatmap,
            "available": True,
            "summary": summary,
        }

    def _build_overview_from_mock(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(patents)
        active = sum(1 for p in patents if p.get("status") == "active")
        expired = sum(1 for p in patents if p.get("status") == "expired")
        pending = sum(1 for p in patents if p.get("status") == "pending")

        active_expiry_dates = [
            p.get("expiry_date") for p in patents
            if p.get("status") == "active" and p.get("expiry_date")
        ]
        earliest_active_expiry = min(active_expiry_dates) if active_expiry_dates else None

        has_fto = expired > 0 or total == 0

        return {
            "total": total,
            "active_count": active,
            "expired_count": expired,
            "pending_count": pending,
            "earliest_active_expiry": earliest_active_expiry,
            "has_any_freedom_to_operate": has_fto,
            "as_of_date": datetime.today().date().isoformat(),
        }

    # ------------ SHARED SUMMARY ------------

    def _build_summary(
        self,
        molecule: str,
        total: int,
        active: int,
        expired: int,
        pending: int,
        earliest_active_expiry: Optional[str],
        source: str,
    ) -> str:
        base = (
            f"Patent landscape for {molecule}: {total} relevant patents identified "
            f"({active} active, {expired} expired, {pending} pending). "
        )
        if earliest_active_expiry:
            base += f"Earliest active patent expiry around {earliest_active_expiry}. "
        base += f"This view is based on {source}."
        return base


# Quick self-test
if __name__ == "__main__":
    agent = PatentLandscapeAgent()
    res = agent.run({"molecule": "metformin", "indication": "NAFLD"})
    print("Available:", res.get("available"))
    print("Overview:", res.get("overview"))
    print("Summary:", res.get("summary"))
    print("Sample patents:", res.get("patents")[:3])
