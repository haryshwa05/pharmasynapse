import json
import os
from typing import Dict, Any, Optional, List
from collections import Counter
from datetime import datetime

from .worker_base import WorkerBase

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "mock_clinical_trials.json"
)


class ClinicalTrialsAgent(WorkerBase):
    """
    Worker Agent that simulates querying ClinicalTrials.gov / WHO ICTRP.
    It returns a structured overview of the trial landscape for a molecule/disease.
    """

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
        query example:
        {
          "molecule": "metformin",
          "disease": "NAFLD"   # optional filter by condition
        }
        """
        molecule = query.get("molecule")
        disease = query.get("disease")

        if not molecule:
            raise ValueError("ClinicalTrialsAgent requires 'molecule' in query")

        entry = self._get_molecule_entry(molecule)
        if not entry:
            return {
                "molecule": molecule,
                "available": False,
                "message": f"No clinical trials mock data found for {molecule}"
            }

        all_trials: List[Dict[str, Any]] = entry.get("trials", [])

        filtered_trials = all_trials
        if disease:
            filtered_trials = [
                t for t in all_trials
                if disease.lower() in t.get("condition", "").lower()
            ]
            # fall back to all trials if filter finds none
            if not filtered_trials:
                filtered_trials = all_trials

        overview = self._build_overview(filtered_trials, all_trials)
        result = {
            "molecule": entry.get("molecule", molecule),
            "filtered_by_disease": disease,
            "trials": filtered_trials,
            "overview": overview,
            "available": True,
            # enriched: sponsor profiles from mock data if present
            "sponsor_profiles": entry.get("sponsor_profiles", []),
        }
        result["summary"] = self._build_summary(result)
        return result

    def _build_overview(
        self,
        filtered_trials: List[Dict[str, Any]],
        all_trials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute distributions by phase, status, sponsor, and how many look like repurposing.
        """
        def count_by_key(trials: List[Dict[str, Any]], key: str) -> Dict[str, int]:
            return dict(Counter(t.get(key, "Unknown") for t in trials))

        phase_dist = count_by_key(filtered_trials, "phase")
        status_dist = count_by_key(filtered_trials, "status")
        sponsor_dist = count_by_key(filtered_trials, "sponsor")

        repurposing_trials = [t for t in filtered_trials if t.get("repurposing_flag")]
        repurposing_count = len(repurposing_trials)

        today = datetime.today().date().isoformat()

        return {
            "total_trials_for_molecule": len(all_trials),
            "trials_in_scope": len(filtered_trials),
            "phase_distribution": phase_dist,
            "status_distribution": status_dist,
            "top_sponsors": sponsor_dist,
            "repurposing_trial_count": repurposing_count,
            "as_of_date": today
        }

    def _build_summary(self, result: Dict[str, Any]) -> str:
        mol = result["molecule"]
        ov = result["overview"]
        disease = result.get("filtered_by_disease")

        scope_text = (
            f"for {mol}"
            + (f" in {disease}" if disease else "")
        )

        txt = (
            f"Clinical trial landscape {scope_text}: "
            f"{ov['trials_in_scope']} trials in scope "
            f"(out of {ov['total_trials_for_molecule']} total for this molecule in the mock dataset). "
        )

        phase_dist = ov["phase_distribution"]
        if phase_dist:
            parts = [f"{p}: {c}" for p, c in phase_dist.items()]
            txt += "Phase distribution – " + ", ".join(parts) + ". "

        status_dist = ov["status_distribution"]
        if status_dist:
            parts = [f"{s}: {c}" for s, c in status_dist.items()]
            txt += "Status mix – " + ", ".join(parts) + ". "

        if ov["repurposing_trial_count"] > 0:
            txt += f"{ov['repurposing_trial_count']} trial(s) appear to be repurposing-focused in this mock dataset."

        return txt


# Quick self-test: python -m app.agents.clinical_trials_agent
if __name__ == "__main__":
    agent = ClinicalTrialsAgent()
    result = agent.run({"molecule": "metformin", "disease": "NAFLD"})
    print("Available:", result.get("available"))
    print("Overview:", result.get("overview"))
    print("Summary:", result.get("summary"))
    print("Trials returned:", len(result.get("trials", [])))
