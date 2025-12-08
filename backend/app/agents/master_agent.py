# master_agent.py
import os
import json
import re
import requests
from typing import Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

# Import sub-agents
from .iqvia_agent import IQVIAInsightsAgent
from .patent_agent import PatentLandscapeAgent
from .clinical_trials_agent import ClinicalTrialsAgent
from .web_intelligence_agent import WebIntelligenceAgent
from .exim_trends_agent import EximTrendsAgent
from .internal_knowledge_agent import InternalKnowledgeAgent


class MasterAgent:
    def __init__(self):
        # Initialize sub agents
        self.iqvia_agent = IQVIAInsightsAgent()
        self.patent_agent = PatentLandscapeAgent()
        self.clinical_agent = ClinicalTrialsAgent()
        self.web_agent = WebIntelligenceAgent()
        self.exim_agent = EximTrendsAgent()
        self.internal_agent = InternalKnowledgeAgent()

        # Gemini config
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not self.gemini_key:
            raise ValueError("Missing GEMINI_API_KEY in .env")

        print(f"[MasterAgent] Using Gemini model: {self.gemini_model}")

    async def handle_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        molecule = query.get("molecule")
        disease = query.get("disease") or query.get("indication")
        region = query.get("region")

        if not molecule:
            raise ValueError("MasterAgent.handle_query requires 'molecule'")

        return self.analyze_molecule(molecule, disease, region)

    def analyze_molecule(self, molecule: str, disease: Optional[str], region: Optional[str]) -> Dict[str, Any]:

        # Run all sub agents
        iqvia = self.iqvia_agent.run({"molecule": molecule, "region": region})
        patents = self.patent_agent.run({"molecule": molecule, "indication": disease})
        trials = self.clinical_agent.run({"molecule": molecule, "disease": disease})
        web = self.web_agent.run({"molecule": molecule, "disease": disease})
        exim = self.exim_agent.run({"molecule": molecule})
        internal = self.internal_agent.run({"molecule": molecule})

        raw = {
            "molecule": molecule,
            "disease": disease,
            "iqvia": iqvia,
            "patents": patents,
            "trials": trials,
            "web": web,
            "exim": exim,
            "internal": internal,
        }

        synthesis = self._synthesize_with_gemini(raw)
        return {**raw, "synthesis": synthesis}

    # -------------------------------------------
    # Extract JSON from Gemini output
    # -------------------------------------------
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None

        # Try direct parse
        try:
            return json.loads(text)
        except:
            pass

        # Extract fenced JSON
        matches = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text)
        for m in matches:
            try:
                return json.loads(m.strip())
            except:
                continue

        # Find first { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            snippet = text[start:end+1]
            try:
                return json.loads(snippet)
            except:
                pass

        return None

    # -------------------------------------------
    # Gemini synthesis
    # -------------------------------------------
    def _synthesize_with_gemini(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"

        system_prompt = (
            "You are a pharmaceutical strategy expert.\n"
            "You MUST return ONLY VALID JSON in this exact structure:\n"
            "{\n"
            '  "executive_summary": "",\n'
            '  "strategic_recommendations": [],\n'
            '  "swot": {\n'
            '     "strengths": [], "weaknesses": [], "opportunities": [], "threats": []\n'
            "  },\n"
            '  "key_insights": {\n'
            '     "market": "", "clinical": "", "patent": "", "supply_chain": ""\n'
            "  }\n"
            "}\n"
            "No markdown, no explanation, no commentary."
        )

        user_prompt = (
            system_prompt
            + "\n\nHere is the data you must analyze:\n"
            + json.dumps(data, indent=2)
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ]
        }

        params = {"key": self.gemini_key}

        try:
            response = requests.post(url, params=params, json=payload, timeout=60)
            print("[Gemini] Status:", response.status_code)

            if response.status_code != 200:
                print("[Gemini] Error:", response.text)
                return self._mock_synthesis(data["molecule"], "Gemini error")

            res = response.json()
            content = res["candidates"][0]["content"]["parts"][0]["text"]
            print("[Gemini] Raw output preview:", content[:300])

            parsed = self._extract_json(content)
            if parsed:
                return parsed

        except Exception as e:
            print("[Gemini] Exception:", e)

        return self._mock_synthesis(data["molecule"], "Gemini failure")


    # -------------------------------------------
    # fallback mock synthesis
    # -------------------------------------------
    def _mock_synthesis(self, molecule: str, error: str = "") -> Dict[str, Any]:
        return {
            "executive_summary": f"Placeholder synthesis for {molecule}. ({error})",
            "strategic_recommendations": ["Improve availability", "Monitor competition", "Optimize supply chain"],
            "swot": {
                "strengths": ["Strong demand"], "weaknesses": ["Pricing pressure"],
                "opportunities": ["New indications"], "threats": ["Generic entrants"]
            },
            "key_insights": {
                "market": "Moderately competitive.",
                "clinical": "Solid efficacy profile.",
                "patent": "Patent situation stable.",
                "supply_chain": "Diversify API sourcing."
            }
        }


# Manual quick test
if __name__ == "__main__":
    ma = MasterAgent()
    out = ma.analyze_molecule("metformin", disease="NAFLD", region="US")
    print(json.dumps(out["synthesis"], indent=2))
