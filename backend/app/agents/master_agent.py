from typing import Dict, Any, Optional

from .iqvia_agent import IQVIAInsightsAgent
from .patent_agent import PatentLandscapeAgent
from .clinical_trials_agent import ClinicalTrialsAgent


class MasterAgent:
    def __init__(self):
        self.iqvia_agent = IQVIAInsightsAgent()
        self.patent_agent = PatentLandscapeAgent()
        self.clinical_agent = ClinicalTrialsAgent()

    def analyze_molecule(
        self,
        molecule: str,
        disease: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:

        iqvia_result = self.iqvia_agent.run({
            "molecule": molecule,
            "region": region
        })

        patent_result = self.patent_agent.run({
            "molecule": molecule,
            "indication": disease
        })

        trials_result = self.clinical_agent.run({
            "molecule": molecule,
            "disease": disease
        })

        return {
            "molecule": molecule,
            "disease": disease,
            "iqvia": iqvia_result,
            "patents": patent_result,
            "trials": trials_result
        }


if __name__ == "__main__":
    ma = MasterAgent()
    out = ma.analyze_molecule("metformin", disease="NAFLD", region="US")
    print("Molecule:", out["molecule"])
    print("IQVIA summary:", out["iqvia"].get("summary"))
    print("Patent summary:", out["patents"].get("summary"))
    print("Trials summary:", out["trials"].get("summary"))
