"""
NLP Agent - Parses free-text strategic prompts using Gemini API.
Converts natural language queries into structured QueryIntent objects.
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai

from app.models.query_intent import QueryIntent, get_workflow_for_intent


# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class NLPAgent:
    """
    Parses natural language strategic questions into structured QueryIntent objects.
    Uses Gemini API for intelligent parsing and entity extraction.
    """
    
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            try:
                # Use Gemini 2.0 (latest experimental model with best performance)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print(f"[NLPAgent] ✓ Initialized with gemini-2.0-flash-exp")
            except Exception as e:
                print(f"[NLPAgent] Failed to initialize Gemini: {e}")
                self.model = None
    
    def parse_prompt(self, prompt: str) -> QueryIntent:
        """
        Main entry point: parse a free-text prompt into QueryIntent.
        
        Args:
            prompt: Natural language strategic question
            
        Returns:
            QueryIntent object with parsed entities and workflow plan
        """
        # If Gemini is available, use it
        if self.model:
            try:
                return self._parse_with_gemini(prompt)
            except Exception as e:
                print(f"[NLPAgent] Gemini parsing failed: {e}, falling back to rule-based")
                return self._parse_with_rules(prompt)
        
        # Fallback to rule-based parsing
        return self._parse_with_rules(prompt)
    
    def _parse_with_gemini(self, prompt: str) -> QueryIntent:
        """Parse prompt using Gemini API for intelligent entity extraction."""
        
        system_prompt = self._build_gemini_prompt(prompt)
        
        response = self.model.generate_content(system_prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response (handles markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        parsed_data = json.loads(response_text)
        
        # Ensure workflow_stages is populated
        if not parsed_data.get("workflow_stages"):
            intent_type = parsed_data.get("intent_type", "strategic_question")
            parsed_data["workflow_stages"] = get_workflow_for_intent(intent_type)
        
        return QueryIntent.from_free_text(prompt, parsed_data)
    
    def _parse_with_rules(self, prompt: str) -> QueryIntent:
        """
        Fallback rule-based parsing when Gemini is not available.
        Uses keyword matching and pattern recognition.
        """
        prompt_lower = prompt.lower()
        
        # Detect intent type
        intent_type = self._detect_intent_type(prompt_lower)
        
        # Extract entities
        molecule = self._extract_molecule(prompt_lower)
        disease = self._extract_disease(prompt_lower)
        geography = self._extract_geography(prompt_lower)
        
        # Build parsed data
        parsed_data = {
            "intent_type": intent_type,
            "primary_entity": molecule,
            "disease_area": disease,
            "geography": geography,
            "workflow_stages": get_workflow_for_intent(intent_type),
            "context": {
                "parsing_method": "rule_based",
                "original_prompt": prompt
            },
            "confidence": 0.6,  # Lower confidence for rule-based
            "parsed_entities": {
                "molecule": molecule,
                "disease": disease,
                "geography": geography
            }
        }
        
        return QueryIntent.from_free_text(prompt, parsed_data)
    
    def _build_gemini_prompt(self, user_prompt: str) -> str:
        """Build the system prompt for Gemini to parse strategic questions."""
        return f"""You are a pharmaceutical intelligence assistant. Parse the user's strategic question and extract structured information.

Analyze this query: "{user_prompt}"

Identify:
1. **Intent Type** (choose one):
   - "molecule_analysis": Analyzing a specific drug/molecule
   - "market_discovery": Finding market opportunities or competitive landscape
   - "repurposing": Exploring new indications for existing molecules
   - "competitive_analysis": Analyzing competition in a space
   - "strategic_question": General strategic insights

2. **Primary Entity**: Extract molecule/drug name if mentioned, else null

3. **Disease Area**: Extract therapeutic area (oncology, diabetes, respiratory, CNS, cardiovascular, etc.) if mentioned

4. **Geography**: Extract country/region (India, US, Europe, China, etc.) if mentioned

5. **Workflow Stages**: Based on intent, suggest which analyses are needed:
   - "iqvia": Market data analysis
   - "clinical_trials": Clinical trial landscape
   - "patent": Patent and IP analysis
   - "exim": Import/export trends
   - "strategic_opportunity": Strategic synthesis and opportunities
   - "web_intelligence": General web research

6. **Context**: Any additional relevant information

Return ONLY valid JSON (no markdown, no explanation):
{{
  "intent_type": "...",
  "primary_entity": "..." or null,
  "disease_area": "..." or null,
  "geography": "..." or null,
  "workflow_stages": ["stage1", "stage2", ...],
  "context": {{}},
  "confidence": 0.9,
  "parsed_entities": {{}}
}}"""
    
    def _detect_intent_type(self, prompt: str) -> str:
        """Detect intent type using keyword matching."""
        
        # Repurposing indicators
        if any(word in prompt for word in ["repurpos", "new indication", "alternative use"]):
            return "repurposing"
        
        # Market discovery indicators
        if any(word in prompt for word in [
            "which disease", "which therapeutic", "opportunity", "unmet need",
            "market gap", "low competition", "patient burden"
        ]):
            return "market_discovery"
        
        # Competitive analysis indicators
        if any(word in prompt for word in ["competition", "competitive", "landscape", "players"]):
            return "competitive_analysis"
        
        # Molecule analysis indicators (look for specific molecule names)
        common_molecules = [
            "metformin", "aspirin", "ibuprofen", "paracetamol", "insulin",
            "atorvastatin", "lisinopril", "amlodipine", "levothyroxine"
        ]
        if any(mol in prompt for mol in common_molecules):
            return "molecule_analysis"
        
        # Default to strategic question
        return "strategic_question"
    
    def _extract_molecule(self, prompt: str) -> Optional[str]:
        """Extract molecule name from prompt."""
        # Common pharmaceutical molecules
        molecules = [
            "metformin", "aspirin", "ibuprofen", "paracetamol", "insulin",
            "atorvastatin", "lisinopril", "amlodipine", "levothyroxine",
            "omeprazole", "simvastatin", "rosuvastatin", "losartan"
        ]
        
        for molecule in molecules:
            if molecule in prompt:
                return molecule.capitalize()
        
        return None
    
    def _extract_disease(self, prompt: str) -> Optional[str]:
        """Extract disease/therapeutic area from prompt."""
        disease_map = {
            "diabetes": ["diabetes", "diabetic", "glycemic"],
            "oncology": ["cancer", "oncology", "tumor", "carcinoma"],
            "cardiovascular": ["cardiovascular", "cardiac", "heart", "hypertension"],
            "respiratory": ["respiratory", "asthma", "copd", "pulmonary"],
            "cns": ["cns", "neurological", "alzheimer", "parkinson", "depression"],
            "nafld": ["nafld", "nash", "fatty liver"],
            "infectious": ["infectious", "antibiotic", "antiviral"]
        }
        
        for disease, keywords in disease_map.items():
            if any(keyword in prompt for keyword in keywords):
                return disease.upper() if disease == "cns" or disease == "nafld" else disease.capitalize()
        
        return None
    
    def _extract_geography(self, prompt: str) -> Optional[str]:
        """Extract geography/region from prompt."""
        geographies = {
            "india": ["india", "indian"],
            "us": ["us", "usa", "united states", "america"],
            "europe": ["europe", "european", "eu"],
            "china": ["china", "chinese"],
            "japan": ["japan", "japanese"],
            "brazil": ["brazil", "brazilian"],
            "global": ["global", "worldwide"]
        }
        
        for geo, keywords in geographies.items():
            if any(keyword in prompt for keyword in keywords):
                return geo.upper() if geo in ["us", "eu"] else geo.capitalize()
        
        return None


# Quick self-test
if __name__ == "__main__":
    agent = NLPAgent()
    
    test_prompts = [
        "Which respiratory diseases show low competition in India?",
        "Is metformin suitable for NAFLD repurposing?",
        "Analyze metformin for diabetes in US market",
        "What are the unmet needs in oncology?",
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        intent = agent.parse_prompt(prompt)
        print(f"Intent Type: {intent.intent_type}")
        print(f"Entity: {intent.primary_entity}")
        print(f"Disease: {intent.disease_area}")
        print(f"Geography: {intent.geography}")
        print(f"Workflow: {intent.workflow_stages}")
        print(f"Confidence: {intent.confidence}")
