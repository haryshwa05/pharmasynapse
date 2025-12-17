"""
QueryIntent Model - Standardized format for all agent interactions.
Supports both free-text prompts and structured inputs.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class QueryIntent:
    """
    Standardized query intent that unifies free-text prompts and structured inputs.
    
    This is the common interface between the NLP parser and all agents.
    """
    
    # Core intent classification
    intent_type: str  # "molecule_analysis", "market_discovery", "repurposing", "strategic_question"
    
    # Primary entities
    primary_entity: Optional[str] = None  # molecule name if mentioned
    disease_area: Optional[str] = None    # therapeutic area
    geography: Optional[str] = None       # country/region
    
    # Original query context
    strategic_question: Optional[str] = None  # original free-text prompt
    is_structured_input: bool = False         # True if from dropdown, False if from prompt
    
    # Workflow execution plan
    workflow_stages: List[str] = field(default_factory=list)  # ["iqvia", "clinical_trials", etc.]
    
    # Additional parsed context
    context: Dict[str, Any] = field(default_factory=dict)  # flexible additional data
    
    # Confidence & metadata
    confidence: float = 1.0  # 0.0-1.0, used by NLP parser
    parsed_entities: Dict[str, Any] = field(default_factory=dict)  # extracted entities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "intent_type": self.intent_type,
            "primary_entity": self.primary_entity,
            "disease_area": self.disease_area,
            "geography": self.geography,
            "strategic_question": self.strategic_question,
            "is_structured_input": self.is_structured_input,
            "workflow_stages": self.workflow_stages,
            "context": self.context,
            "confidence": self.confidence,
            "parsed_entities": self.parsed_entities,
        }
    
    @classmethod
    def from_structured_input(
        cls,
        molecule: str,
        disease: Optional[str] = None,
        region: Optional[str] = None
    ) -> "QueryIntent":
        """
        Create QueryIntent from traditional structured input (dropdown selections).
        This maintains backward compatibility with existing API.
        """
        return cls(
            intent_type="molecule_analysis",
            primary_entity=molecule,
            disease_area=disease,
            geography=region,
            is_structured_input=True,
            workflow_stages=["iqvia", "exim", "clinical_trials", "patent"],
            confidence=1.0
        )
    
    @classmethod
    def from_free_text(
        cls,
        prompt: str,
        parsed_data: Dict[str, Any]
    ) -> "QueryIntent":
        """
        Create QueryIntent from NLP-parsed free-text prompt.
        """
        return cls(
            intent_type=parsed_data.get("intent_type", "strategic_question"),
            primary_entity=parsed_data.get("primary_entity"),
            disease_area=parsed_data.get("disease_area"),
            geography=parsed_data.get("geography"),
            strategic_question=prompt,
            is_structured_input=False,
            workflow_stages=parsed_data.get("workflow_stages", []),
            context=parsed_data.get("context", {}),
            confidence=parsed_data.get("confidence", 0.8),
            parsed_entities=parsed_data.get("parsed_entities", {})
        )


# Workflow stage definitions
WORKFLOW_TEMPLATES = {
    "molecule_analysis": [
        "iqvia",
        "exim", 
        "clinical_trials",
        "patent"
    ],
    
    "market_discovery": [
        "iqvia",
        "clinical_trials",
        "exim",
        "strategic_opportunity"
    ],
    
    "repurposing": [
        "molecule_profile",
        "unmet_needs",
        "clinical_trials",
        "patent",
        "market_attractiveness",
        "strategic_opportunity"
    ],
    
    "strategic_question": [
        "web_intelligence",
        "strategic_opportunity"
    ],
    
    "competitive_analysis": [
        "iqvia",
        "clinical_trials",
        "patent",
        "strategic_opportunity"
    ]
}


def get_workflow_for_intent(intent_type: str) -> List[str]:
    """Get the default workflow stages for a given intent type."""
    return WORKFLOW_TEMPLATES.get(intent_type, ["strategic_opportunity"])
