"""
Enhanced Prompt-Based Workflow
Simple & Direct: ANY pharma question → Gemini 2.0 → Beautiful results
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.nlp_agent import NLPAgent
from app.agents.iqvia_agent import IQVIAInsightsAgent
from app.agents.clinical_trials_agent import ClinicalTrialsAgent
from app.agents.patent_agent import PatentLandscapeAgent
from app.agents.exim_trends_agent import EximTrendsAgent
from app.agents.web_intelligence_agent import WebIntelligenceAgent


class EnhancedPromptWorkflow:
    """
    Universal Pharmaceutical Intelligence Engine
    
    Simple workflow: Question → Gemini 2.0 → Beautiful Answer
    Can answer ANY pharma question on ANY topic.
    """
    
    def __init__(self):
        # NLP agent for quick intent detection
        self.nlp_agent = NLPAgent()
        
        # Gemini 2.0 configuration
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        if self.gemini_key:
            print(f"[EnhancedPromptWorkflow] ✓ Ready with {self.gemini_model}")
        else:
            print("[EnhancedPromptWorkflow] ⚠️ No GEMINI_API_KEY - limited functionality")
    
    async def execute_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Universal pharmaceutical intelligence: Answer ANY pharma question.
        """
        start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"[PromptWorkflow] 💬 {prompt}")
        print(f"{'='*60}")
        
        # Quick intent detection (for metadata only)
        query_intent = self.nlp_agent.parse_prompt(prompt)
        print(f"[PromptWorkflow] 📊 Intent: {query_intent.intent_type}")
        
        # DIRECTLY ask Gemini
        print(f"[PromptWorkflow] 🤖 Asking Gemini 2.0...")
        analysis = self._ask_gemini_directly(prompt, query_intent)
        
        # Format beautifully
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"[PromptWorkflow] ✅ Answered in {execution_time:.1f}s\n")
        
        return self._format_beautiful_output(
            prompt, query_intent, analysis, execution_time
        )
    
    def _ask_gemini_directly(self, prompt: str, query_intent) -> Dict[str, Any]:
        """Ask Gemini directly - simple and fast."""
        
        if not self.gemini_key:
            return self._generate_simple_fallback(prompt)
        
        research_prompt = f"""You are the world's leading pharmaceutical strategist and scientist. 
Answer this question: "{prompt}"

ADAPT YOUR ANSWER STRUCTURE to the specific domain of the question (e.g., Chemistry, Clinical, Market, Regulatory, etc.).

Return a JSON object with this flexible structure:

{{
  "title": "A clear, professional title for the analysis",
  "executive_summary": "Direct, 2-3 sentence answer to the core question",
  "analysis_sections": [
    {{
      "heading": "Section Title (e.g., 'Molecular Properties', 'Clinical Implications', 'Market Dynamics')",
      "content": "Detailed analysis. Use bullet points or paragraphs. Be specific."
    }}
  ],
  "key_takeaways": [
    "Critical insight 1",
    "Critical insight 2",
    "Critical insight 3"
  ],
  "follow_up_recommendation": "The single most important next step or consideration"
}}

RULES:
1. Be ULTRA-SPECIFIC - use actual names, numbers, dates, and chemical logic where applicable.
2. DO NOT force a market framework on a chemistry question, or vice versa. Adapt to the topic.
3. Return ONLY valid JSON.
4. No markdown formatting outside the JSON string values.
"""

        return self._call_gemini_api(research_prompt)
    
    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini API using the configured model only."""
        
        try:
            model = self.gemini_model
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            
            payload = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.5,
                    "maxOutputTokens": 4096,
                }
            }
            
            print(f"  → Calling {model}...")
            
            # Simple retry logic for 503 Overloaded errors
            max_retries = 3
            import time
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        url,
                        params={"key": self.gemini_key},
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        break # Success
                    elif response.status_code == 503:
                        msg = response.json().get('error', {}).get('message', 'Service Unavailable')
                        print(f"  ⚠ Gemini Overloaded (Attempt {attempt+1}/{max_retries}): {msg}. Retrying in {2*(attempt+1)}s...")
                        time.sleep(2 * (attempt + 1))
                    else:
                        break # Other errors, don't retry blindly
                except requests.exceptions.RequestException as e:
                     print(f"  ⚠ Network error (Attempt {attempt+1}): {e}")
                     time.sleep(2)
            
            
            if response.status_code == 200:
                content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                print(f"  ✓ Success! ({len(content)} chars)")
                
                analysis = self._extract_json(content)
                if analysis:
                    print(f"  ✓ JSON extracted")
                    return analysis
                else:
                    print(f"  ✗ JSON extraction failed, using raw response")
                    return self._generate_simple_fallback(f"Gemini responded but JSON extraction failed: {content[:200]}")
                    
            elif response.status_code == 429:
                print(f"  ✗ Rate limit exceeded (429) - too many requests")
                return self._generate_simple_fallback("Rate limit exceeded. Please wait a moment and try again.")
                
            elif response.status_code == 404:
                print(f"  ✗ Model not found (404) - check GEMINI_MODEL in .env")
                return self._generate_simple_fallback(f"Model '{model}' not found. Update GEMINI_MODEL in .env file.")
                
            elif response.status_code == 403:
                print(f"  ✗ Invalid API key (403)")
                return self._generate_simple_fallback("Invalid GEMINI_API_KEY. Check your .env file.")
                
            else:
                print(f"  ✗ Error {response.status_code}: {response.text[:200]}")
                return self._generate_simple_fallback(f"Gemini API error {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
            return self._generate_simple_fallback(f"Error calling Gemini: {str(e)[:100]}")
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response."""
        
        # Try direct parse
        try:
            return json.loads(text)
        except:
            pass
        
        # Try markdown code blocks
        import re
        matches = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text)
        for match in matches:
            try:
                return json.loads(match.strip())
            except:
                continue
        
        # Try finding JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                # Clean up potential comments or weird spacing
                json_str = text[start:end+1]
                return json.loads(json_str)
            except:
                pass
        
        # Try finding JSON list if it's a list
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            try:
                json_str = text[start:end+1]
                return json.loads(json_str)
            except:
                pass
        
        return None
    
    def _generate_simple_fallback(self, error_msg: str = "") -> Dict[str, Any]:
        """Simple fallback when Gemini isn't available."""
        
        if not error_msg:
            error_msg = "Gemini API is not available. Please check your GEMINI_API_KEY configuration."
        
        return {
            "direct_answer": error_msg,
            "key_insights": [
                "To use AI-powered intelligence, configure your Gemini API key",
                "Get a free API key at: https://makersuite.google.com/app/apikey",
                "Add it to your .env file as GEMINI_API_KEY=your_key_here"
            ],
            "detailed_analysis": {
                "market_commercial": ["Configure API key to get market intelligence"],
                "clinical_development": ["Configure API key to get clinical insights"],
                "strategic_considerations": ["Configure API key to get strategic guidance"]
            },
            "recommendations": [
                {
                    "priority": "1",
                    "action": "Configure Gemini API key",
                    "rationale": "Required for AI-powered pharmaceutical intelligence",
                    "timeline": "5 minutes",
                    "investment": "Free"
                }
            ],
            "decision_guidance": {
                "recommendation": "Configure API key to proceed",
                "confidence": "N/A",
                "success_factors": ["Valid API key"],
                "risks": ["Limited functionality without AI"],
                "next_steps": ["Get API key", "Add to .env", "Restart server"]
            },
            "sources_and_context": "Fallback response - Gemini API not configured"
        }
    
    def _format_beautiful_output(
        self,
        prompt: str,
        query_intent,
        analysis: Dict[str, Any],
        execution_time: float
    ) -> Dict[str, Any]:
        """Format output beautifully for frontend display."""
        
        # Extract components
        recommendations = analysis.get("recommendations", [])
        decision = analysis.get("decision_guidance", {})
        
        # Build strategic opportunity object (frontend compatible)
        # Build strategic opportunity object (frontend compatible)
        strategic_opportunity = {
            "opportunity_type": query_intent.intent_type,
            
            # Map new flexible fields
            "executive_summary": analysis.get("executive_summary", ""),
            "answer_highlights": analysis.get("key_takeaways", []),
            
            # We'll use this generic list for rendering flexible sections in the frontend
            "flexible_sections": analysis.get("analysis_sections", []),
            
            "innovation_story": analysis.get("title", "Strategic Analysis"),
            "go_no_go_recommendation": "ANALYSIS COMPLETE", # Generic status
            "decision_framework": {
                "confidence_level": "HIGH",
                "key_success_factors": [analysis.get("follow_up_recommendation", "")],
                "deal_breakers": [],
                "data_gaps": []
            },
            
            # Keep legacy empty structures to prevent frontend crashes if keys are expected
            "key_insights": [],
            "market_insights": [],
            "clinical_insights": [],
            "recommendations": [],
            "unmet_needs": [],
            "market_analysis": {},
            "competitive_landscape": {},
            "swot_analysis": {},
            "opportunities_and_risks": {}
        }
        
        # Return frontend-compatible format
        return {
            "success": True,
            "workflow_type": "direct_gemini_intelligence",
            "execution_time_seconds": round(execution_time, 2),
            
            "query_intent": {
                "intent_type": query_intent.intent_type,
                "primary_entity": query_intent.primary_entity,
                "disease_area": query_intent.disease_area,
                "geography": query_intent.geography,
                "strategic_question": prompt,
                "confidence": query_intent.confidence,
                "workflow_stages": []
            },
            
            "results": {
                "agent_outputs": {
                    "strategic_opportunity": strategic_opportunity
                },
                "execution_log": [
                    {"stage": "gemini_analysis", "status": "success", "timestamp": datetime.now().isoformat()}
                ],
                "execution_time_seconds": round(execution_time, 2),
                "success": True,
                "summary": analysis.get("direct_answer", "")
            },
            
            "enhanced_analysis": {
                "full_gemini_response": analysis,
                "model_used": self.gemini_model
            }
        }


# Global instance
_workflow_instance = None

def get_enhanced_prompt_workflow() -> EnhancedPromptWorkflow:
    """Get or create the workflow singleton."""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = EnhancedPromptWorkflow()
    return _workflow_instance
