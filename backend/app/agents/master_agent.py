from typing import Dict, Any, Optional

from .iqvia_agent import IQVIAInsightsAgent
from .patent_agent import PatentLandscapeAgent
from .clinical_trials_agent import ClinicalTrialsAgent
from .web_intelligence_agent import WebIntelligenceAgent
from .exim_trends_agent import EximTrendsAgent
from .internal_knowledge_agent import InternalKnowledgeAgent


class MasterAgent:
    def __init__(self):
        self.iqvia_agent = IQVIAInsightsAgent()
        self.patent_agent = PatentLandscapeAgent()
        self.clinical_agent = ClinicalTrialsAgent()
        self.web_agent = WebIntelligenceAgent()
        self.exim_agent = EximTrendsAgent()
        self.internal_agent = InternalKnowledgeAgent()

    async def handle_query(
        self,
        query: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Async wrapper used by API; normalizes fields and delegates to analyze_molecule.
        """
        molecule = query.get("molecule")
        disease = query.get("disease") or query.get("indication")
        region = query.get("region")

        if not molecule:
            raise ValueError("MasterAgent.handle_query requires 'molecule'")

        return self.analyze_molecule(
            molecule=molecule,
            disease=disease,
            region=region,
        )

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

        web_result = self.web_agent.run({
            "molecule": molecule,
            "disease": disease
        })

        exim_result = self.exim_agent.run({
            "molecule": molecule,
        })

        internal_result = self.internal_agent.run({
            "molecule": molecule,
        })

        return {
            "molecule": molecule,
            "disease": disease,
            "iqvia": iqvia_result,
            "patents": patent_result,
            "trials": trials_result,
            "web": web_result,
            "exim": exim_result,
            "internal": internal_result,
        }


if __name__ == "__main__":
    ma = MasterAgent()
    out = ma.analyze_molecule("metformin", disease="NAFLD", region="US")
    print("Molecule:", out["molecule"])
    print("IQVIA summary:", out["iqvia"].get("summary"))
    print("Patent summary:", out["patents"].get("summary"))
    print("Trials summary:", out["trials"].get("summary"))

