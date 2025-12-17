# master_agent.py
import os
import json
import re
import requests
from typing import Dict, Any, Optional, Union

from dotenv import load_dotenv
load_dotenv()

# Import sub-agents (legacy)
from .iqvia_agent import IQVIAInsightsAgent
from .patent_agent import PatentLandscapeAgent
from .clinical_trials_agent import ClinicalTrialsAgent
from .web_intelligence_agent import WebIntelligenceAgent
from .exim_trends_agent import EximTrendsAgent
from .internal_knowledge_agent import InternalKnowledgeAgent

# Import new infrastructure
from app.models.query_intent import QueryIntent
from app.workflow.orchestrator import WorkflowOrchestrator
from app.agents.nlp_agent import NLPAgent


class MasterAgent:
    """
    Enhanced MasterAgent supporting both:
    1. Legacy structured input (molecule + disease + region)
    2. New prompt-based input with multi-stage workflows
    """
    
    def __init__(self):
        # Legacy sub agents (for backward compatibility)
        self.iqvia_agent = IQVIAInsightsAgent()
        self.patent_agent = PatentLandscapeAgent()
        self.clinical_agent = ClinicalTrialsAgent()
        self.web_agent = WebIntelligenceAgent()
        self.exim_agent = EximTrendsAgent()
        self.internal_agent = InternalKnowledgeAgent()

        # New infrastructure
        self.workflow_orchestrator = WorkflowOrchestrator()
        self.nlp_agent = NLPAgent()

        # Gemini config
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not self.gemini_key:
            print("[MasterAgent] WARNING: GEMINI_API_KEY not found, synthesis features limited")

        print(f"[MasterAgent] Initialized with multi-stage workflow support")

    async def handle_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle query - supports both structured and prompt inputs.
        
        Args:
            query: Can contain:
                - Structured: {"molecule": "...", "disease": "...", "region": "..."}
                - Prompt: {"prompt": "free text strategic question"}
        """
        # Check if this is a prompt-based query
        if "prompt" in query:
            return await self.handle_prompt_query(query["prompt"])
        
        # Legacy structured input
        molecule = query.get("molecule")
        disease = query.get("disease") or query.get("indication")
        region = query.get("region")

        if not molecule:
            raise ValueError("MasterAgent.handle_query requires 'molecule' or 'prompt'")

        return self.analyze_molecule(molecule, disease, region)
    
    async def handle_prompt_query(self, prompt: str) -> Dict[str, Any]:
        """
        NEW: Handle free-text strategic prompt.
        
        Args:
            prompt: Natural language strategic question
            
        Returns:
            Multi-stage workflow results
        """
        # Step 1: Parse prompt with NLP Agent
        query_intent = self.nlp_agent.parse_prompt(prompt)
        
        print(f"[MasterAgent] Parsed intent: {query_intent.intent_type}")
        print(f"[MasterAgent] Workflow stages: {query_intent.workflow_stages}")
        
        # Step 2: Execute workflow
        workflow_result = self.workflow_orchestrator.execute(query_intent)
        
        # Step 3: Add Gemini synthesis if available
        if self.gemini_key:
            try:
                gemini_synthesis = self._synthesize_with_gemini(workflow_result)
                workflow_result["gemini_synthesis"] = gemini_synthesis
            except Exception as e:
                print(f"[MasterAgent] Gemini synthesis failed: {e}")
                workflow_result["gemini_synthesis"] = self._mock_synthesis(
                    query_intent.primary_entity or "unknown",
                    "Gemini synthesis failed"
                )
        
        return workflow_result

    def analyze_molecule(
        self, 
        molecule: str, 
        disease: Optional[str], 
        region: Optional[str],
        use_new_workflow: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze molecule using either legacy or new workflow.
        
        Args:
            molecule: Molecule name
            disease: Disease/indication
            region: Geographic region
            use_new_workflow: If True, use new orchestrator; if False, use legacy
        """
        
        if use_new_workflow:
            # Use new workflow orchestrator
            query_intent = QueryIntent.from_structured_input(
                molecule=molecule,
                disease=disease,
                region=region
            )
            return self.workflow_orchestrator.execute(query_intent)
        
        # Legacy workflow - maintain backward compatibility
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
            # Retry logic for 503
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, params=params, json=payload, timeout=60)
                    if response.status_code == 200:
                        break
                    elif response.status_code == 503:
                        print(f"[Gemini] 503 Overloaded (Attempt {attempt+1}). Retrying...")
                        time.sleep(2 * (attempt + 1))
                    else:
                        break 
                except requests.exceptions.RequestException as e:
                    print(f"[Gemini] Network error (Attempt {attempt+1}): {e}")
                    time.sleep(1)

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
