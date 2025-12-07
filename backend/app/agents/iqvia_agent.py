import json
import os
from typing import Dict, Any, Optional

from .worker_base import WorkerBase

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock_iqvia.json")


class IQVIAInsightsAgent(WorkerBase):
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
          "region": "US"   # optional
        }
        """
        molecule = query.get("molecule")
        region = query.get("region")

        if not molecule:
            raise ValueError("IQVIAInsightsAgent requires 'molecule' in query")

        entry = self._get_molecule_entry(molecule)
        if not entry:
            return {
                "molecule": molecule,
                "available": False,
                "message": f"No IQVIA mock data found for {molecule}"
            }

        regions = entry.get("regions", {})
        if region and region in regions:
            selected_region = {region: regions[region]}
        else:
            selected_region = regions  # return all if region not specified

        # This is the structured output your master agent & report will use
        result = {
            "molecule": entry.get("molecule", molecule),
            "atc_class": entry.get("atc_class"),
            "regions": selected_region,
            "therapy_dynamics": entry.get("therapy_dynamics", []),
            "available": True
        }

        # Optional: pre-compute a tiny text summary to drop into the report.
        result["summary"] = self._build_summary(result)

        return result

    def _build_summary(self, result: Dict[str, Any]) -> str:
        molecule = result["molecule"]
        regions = result["regions"]

        parts = [f"Market overview for {molecule}:"]
        for region_name, rdata in regions.items():
            ms = rdata.get("market_size_usd_mn")
            cagr = rdata.get("cagr_5y_percent")
            comp_count = len(rdata.get("competitors", []))
            parts.append(
                f"- {region_name}: ~${ms}M, {cagr}% CAGR, about {comp_count} key competitors."
            )

        if result.get("therapy_dynamics"):
            parts.append("Therapy dynamics: " + "; ".join(result["therapy_dynamics"]))

        return " ".join(parts)
    
    
if __name__ == "__main__":
    agent = IQVIAInsightsAgent()
    result = agent.run({"molecule": "metformin", "region": "US"})
    print("Available:", result.get("available"))
    print("Summary:", result.get("summary"))
    print("Regions:", list(result.get("regions", {}).keys()))
