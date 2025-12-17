# PharmaSynapse - Strategic Intelligence Platform Implementation Plan

## 🎯 Objective
Transform the current molecule analysis system into a full strategic pharma intelligence platform that accepts:
1. **Free-text prompts**: "Which respiratory diseases show low competition in India?"
2. **Structured inputs**: Molecule + Disease + Region (backward compatible)

## 📋 Architecture Overview

```
User Input (Free-text OR Structured)
    ↓
NLP Agent (Gemini) → QueryIntent (standardized format)
    ↓
MasterAgent (Multi-stage Workflow Orchestrator)
    ↓
├── Stage 1: Molecule Discovery
├── Stage 2: Unmet Needs Analysis
├── Stage 3: Repurposing Opportunities
├── Stage 4: Clinical Trial Landscape
├── Stage 5: Patent/FTO Analysis
└── Stage 6: Strategic Opportunity Report
    ↓
Report Generator (5-slide journey)
```

## 🏗️ Implementation Steps

### **PHASE 1: Core Infrastructure (Foundation)**

#### 1.1 QueryIntent Model (Standardized Format)
**File**: `backend/app/models/query_intent.py` (NEW)

```python
class QueryIntent:
    intent_type: str  # "molecule_analysis", "market_discovery", "repurposing", "strategic_question"
    primary_entity: str  # molecule name or None
    disease_area: str | None
    geography: str | None
    strategic_question: str | None
    workflow_stages: List[str]  # which agents to invoke
    context: Dict[str, Any]  # additional parsed context
```

#### 1.2 NLP Agent with Gemini
**File**: `backend/app/agents/nlp_agent.py` (NEW)

**Responsibilities**:
- Parse free-text prompts using Gemini API
- Extract entities (molecules, diseases, regions)
- Identify intent type
- Return QueryIntent object

**Example flows**:
```
"Which respiratory diseases show low competition in India?"
→ QueryIntent(
    intent_type="market_discovery",
    disease_area="respiratory",
    geography="India",
    workflow_stages=["iqvia", "exim", "clinical_trials", "strategic_opportunity"]
)

"Is metformin suitable for NAFLD repurposing?"
→ QueryIntent(
    intent_type="repurposing",
    primary_entity="metformin",
    disease_area="NAFLD",
    workflow_stages=["clinical_trials", "patent", "strategic_opportunity"]
)

"Metformin analysis for diabetes in US"
→ QueryIntent(
    intent_type="molecule_analysis",
    primary_entity="metformin",
    disease_area="diabetes",
    geography="US",
    workflow_stages=["iqvia", "exim", "clinical_trials", "patent"]
)
```

### **PHASE 2: Multi-Stage Workflow Engine**

#### 2.1 Workflow Orchestrator
**File**: `backend/app/workflow/orchestrator.py` (NEW)

**Responsibilities**:
- Accept QueryIntent
- Determine execution pipeline based on intent_type
- Execute stages sequentially with context passing
- Aggregate results

**Workflow Types**:

1. **Molecule Analysis** (current system)
   - IQVIA → EXIM → Clinical Trials → Patents → Report

2. **Market Discovery**
   - IQVIA (disease landscape) → Clinical Trials → Strategic Opportunity → Report

3. **Repurposing Workflow** (NEW - Critical!)
   - Stage 1: Molecule profile (mechanism, indications)
   - Stage 2: Unmet needs in target disease
   - Stage 3: Trial activity for new indication
   - Stage 4: Patent constraints (FTO)
   - Stage 5: Market attractiveness
   - Stage 6: Strategic opportunity synthesis

#### 2.2 Update MasterAgent
**File**: `backend/app/agents/master_agent.py` (MODIFY)

**Changes**:
- Accept QueryIntent instead of just Dict
- Support multi-stage workflows
- Pass context between stages
- Maintain backward compatibility with current API

### **PHASE 3: Strategic Opportunity Engine**

#### 3.1 Strategic Opportunity Agent
**File**: `backend/app/agents/strategic_opportunity_agent.py` (NEW)

**Responsibilities**:
- Synthesize data from all worker agents
- Identify unmet needs
- Suggest repurposing opportunities
- Evaluate market attractiveness
- Generate innovation narrative

**Output**:
```python
{
    "opportunity_type": "repurposing" | "market_entry" | "lifecycle_extension",
    "unmet_needs": [...],
    "proposed_indications": [...],
    "innovation_story": "...",
    "market_potential": {...},
    "feasibility_score": 0.0-1.0,
    "key_insights": [...],
    "recommendations": [...]
}
```

### **PHASE 4: Enhanced Worker Agents**

#### 4.1 Update All Worker Agents
**Files**: All `*_agent.py` files (MODIFY)

**Changes**:
- Accept QueryIntent as input (alongside current Dict for backward compat)
- Extract relevant fields from QueryIntent
- Support partial/optional inputs
- Return richer insights for strategic synthesis

#### 4.2 New Molecule Discovery Agent
**File**: `backend/app/agents/molecule_discovery_agent.py` (NEW)

**Responsibilities**:
- When no molecule specified, suggest candidates
- Based on disease area, mechanism, market criteria
- Use mock data or web intelligence

### **PHASE 5: API Layer**

#### 5.1 New Prompt Endpoint
**File**: `backend/app/api/prompt_routes.py` (NEW)

```python
@router.post("/prompt/analyze")
async def analyze_prompt(prompt: str):
    # 1. Parse with NLP Agent → QueryIntent
    # 2. Execute workflow via Orchestrator
    # 3. Return results
```

#### 5.2 Update Existing Routes
**File**: `backend/app/api/routes.py` (MODIFY)

- Keep `/api/analyze` for structured input
- Convert structured input → QueryIntent
- Use same Orchestrator backend

### **PHASE 6: Report Enhancement**

#### 6.1 5-Slide Journey Report
**File**: `backend/app/report/report_generator.py` (MODIFY)

**New slide types**:
- Slide 1: Strategic Question & Context
- Slide 2: Agent Decomposition & Data Sources
- Slide 3: Data Synthesis (IQVIA, EXIM, Patents, Trials)
- Slide 4: Strategic Opportunity & Innovation Story
- Slide 5: Recommendations & Next Steps

### **PHASE 7: Frontend Integration**

#### 7.1 Prompt Input Component
**File**: `frontend/src/components/PromptInput.tsx` (NEW)

- Free-text textarea
- Submit button
- Example prompts
- Loading states

#### 7.2 Update Main Analysis Page
**File**: `frontend/src/pages/Analysis.tsx` (MODIFY)

- Add tab switcher: "Quick Analysis" vs "Strategic Prompt"
- Keep existing dropdowns for structured input
- Add new prompt interface

## 🔧 Technical Implementation Details

### Gemini API Integration

**Environment Variable**:
```bash
GEMINI_API_KEY=your_gemini_api_key
```

**Prompt Template for NLP Agent**:
```
You are a pharmaceutical intelligence assistant. Parse the user's strategic question and extract:

1. Intent type: [molecule_analysis, market_discovery, repurposing, strategic_question]
2. Primary entity: [molecule name if mentioned, else null]
3. Disease area: [therapeutic area if mentioned]
4. Geography: [country/region if mentioned]
5. Workflow stages needed: [list of required analyses]

User query: "{user_prompt}"

Return JSON format:
{
  "intent_type": "...",
  "primary_entity": "..." or null,
  "disease_area": "..." or null,
  "geography": "..." or null,
  "strategic_question": "original query",
  "workflow_stages": ["..."],
  "extracted_context": {...}
}
```

### Workflow Stage Mapping

```python
WORKFLOW_TEMPLATES = {
    "molecule_analysis": ["iqvia", "exim", "clinical_trials", "patent", "report"],
    "market_discovery": ["iqvia", "clinical_trials", "strategic_opportunity", "report"],
    "repurposing": [
        "molecule_profile",
        "unmet_needs",
        "clinical_trials",
        "patent",
        "market_attractiveness",
        "strategic_opportunity",
        "report"
    ],
    "strategic_question": ["web_intelligence", "strategic_opportunity", "report"]
}
```

## 📦 New Dependencies

Add to `requirements.txt`:
```
google-generativeai  # Gemini API
```

## 🎯 Success Criteria

✅ Accept both free-text prompts and structured inputs
✅ NLP agent correctly parses strategic questions
✅ Multi-stage repurposing workflow functional
✅ Strategic opportunity engine generates insights
✅ 5-slide report with full journey narrative
✅ Backward compatible with existing functionality

## 📊 Example End-to-End Flow

### Input: "Which respiratory diseases show low competition in India?"

1. **NLP Agent** → QueryIntent(market_discovery, respiratory, India)
2. **Orchestrator** → Execute market_discovery workflow
3. **IQVIA Agent** → Disease landscape in respiratory (India)
4. **Clinical Trials Agent** → Active trials in respiratory (India)
5. **EXIM Agent** → Import/export trends for respiratory drugs (India)
6. **Strategic Opportunity Agent** → Synthesize gaps, suggest opportunities
7. **Report Generator** → 5-slide PDF with opportunity narrative

### Output:
```json
{
  "strategic_question": "Which respiratory diseases show low competition in India?",
  "identified_opportunities": [
    {
      "disease": "COPD",
      "competition_level": "low",
      "market_size": "$X million",
      "unmet_needs": ["..."],
      "recommended_approach": "..."
    }
  ],
  "report_url": "/reports/market_discovery_xyz.pdf"
}
```

## 🚀 Implementation Order

1. ✅ QueryIntent model
2. ✅ NLP Agent with Gemini
3. ✅ Workflow Orchestrator
4. ✅ Strategic Opportunity Agent
5. ✅ Update MasterAgent
6. ✅ Update worker agents
7. ✅ New API endpoints
8. ✅ Report enhancements
9. ✅ Frontend updates
10. ✅ Testing & validation

---

**Estimated Time**: 4-6 hours for core functionality
**Priority**: High - addresses critical hackathon requirements
