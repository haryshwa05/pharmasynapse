import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from .worker_base import WorkerBase

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "mock_patents.json"
)


class PatentLandscapeAgent(WorkerBase):
    def __init__(self, data_path: str = DATA_FILE):
        self.data_path = data_path
        self._cache = None

    def _load_data(self) -> Dict[str, Any]:
        if self._cache is None:
            with open(self.data_path, "r") as f:
                self._cache = json.load(f)
        return self._cache

    def _get_molecule_entry(self, molecule: str) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        return data.get(molecule.lower())

    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        query = {
          "molecule": "metformin",
          "indication": "NAFLD"  # optional
        }
        """
        molecule = query.get("molecule")
        if not molecule:
            raise ValueError("PatentLandscapeAgent requires 'molecule' in query")

        entry = self._get_molecule_entry(molecule)
        if not entry:
            return {
                "molecule": molecule,
                "available": False,
                "message": f"No patent mock data found for {molecule}"
            }

        patents: List[Dict[str, Any]] = entry.get("patents", [])
        overview = self._summarise_patent_status(patents)

        result = {
            "molecule": entry.get("molecule", molecule),
            "patents": patents,
            "overview": overview,
            "available": True
        }
        result["summary"] = self._build_summary(result)
        return result

    def _summarise_patent_status(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        today = datetime.today().date()

        active = [p for p in patents if p.get("status") == "active"]
        expired = [p for p in patents if p.get("status") == "expired"]
        pending = [p for p in patents if p.get("status") == "pending"]

        earliest_expiry = None
        if active:
            dates = []
            for p in active:
                try:
                    dates.append(datetime.strptime(p["expiry_date"], "%Y-%m-%d").date())
                except Exception:
                    continue
            if dates:
                earliest_expiry = min(dates).isoformat()

        return {
            "total": len(patents),
            "active_count": len(active),
            "expired_count": len(expired),
            "pending_count": len(pending),
            "earliest_active_expiry": earliest_expiry,
            "has_any_freedom_to_operate": len(active) == 0 or len(expired) > 0,
            "as_of_date": today.isoformat()
        }

    def _build_summary(self, result: Dict[str, Any]) -> str:
        mol = result["molecule"]
        ov = result["overview"]
        txt = (
            f"Patent landscape for {mol}: {ov['total']} relevant patents identified, "
            f"{ov['active_count']} active, {ov['expired_count']} expired, "
            f"{ov['pending_count']} pending."
        )
        if ov["earliest_active_expiry"]:
            txt += f" Earliest active patent expiry around {ov['earliest_active_expiry']}."
        if ov["has_any_freedom_to_operate"]:
            txt += " There appears to be at least partial freedom-to-operate in this mock dataset."
        else:
            txt += " Current landscape suggests limited freedom-to-operate."
        return txt


# quick self-test, same style as IQVIA
if __name__ == "__main__":
    agent = PatentLandscapeAgent()
    result = agent.run({"molecule": "metformin"})
    print("Available:", result.get("available"))
    print("Overview:", result.get("overview"))
    print("Summary:", result.get("summary"))
