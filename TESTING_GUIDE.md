# PharmaSynapse - Testing Guide

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
GEMINI_API_KEY=your_gemini_api_key
PATENTSVIEW_API_KEY=your_patentsview_api_key

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## 🧪 Testing the New Features

### Test 1: Structured Input (Legacy - Backward Compatibility)

**Purpose**: Verify existing functionality still works

1. Open `http://localhost:3000`
2. Select **"🔍 Quick Analysis"** tab
3. Fill in:
   - Molecule: `metformin`
   - Disease: `NAFLD`
   - Region: `US`
4. Click **"Run Agent"**
5. Wait for analysis to complete (~5-10 seconds)
6. Verify:
   - ✅ Executive summary appears
   - ✅ SWOT analysis displayed
   - ✅ Data from all agents (IQVIA, Patents, Trials, EXIM, Web)

### Test 2: Prompt-Based Market Discovery

**Purpose**: Test free-text prompt with market discovery intent

1. Select **"💬 Strategic Prompt"** tab
2. Enter prompt: 
   ```
   Which respiratory diseases show low competition in India?
   ```
3. Click **"🚀 Analyze Prompt"**
4. Verify:
   - ✅ Query intent correctly identified as "market_discovery"
   - ✅ Disease area extracted: "respiratory"
   - ✅ Geography extracted: "India"
   - ✅ Workflow execution log shows: IQVIA → Clinical Trials → Strategic Opportunity
   - ✅ Strategic opportunity card shows insights
   - ✅ Unmet needs identified

**Expected Output**:
- Intent Type: market_discovery
- Workflow stages: iqvia, clinical_trials, strategic_opportunity
- Innovation story about respiratory opportunities in India

### Test 3: Repurposing Workflow

**Purpose**: Test drug repurposing evaluation

1. Select **"💬 Strategic Prompt"** tab
2. Enter prompt:
   ```
   Is metformin suitable for NAFLD repurposing?
   ```
3. Click **"🚀 Analyze Prompt"**
4. Verify:
   - ✅ Intent type: "repurposing"
   - ✅ Molecule: "Metformin"
   - ✅ Disease area: "NAFLD"
   - ✅ **Feasibility Score** displayed (0.0-1.0)
   - ✅ Innovation story explains repurposing opportunity
   - ✅ Recommendations section with actionable next steps
   - ✅ Unmet needs section populated
   - ✅ Trial activity analysis
   - ✅ Patent FTO assessment

**Expected Feasibility Breakdown**:
- Trial Activity: Low/Moderate (3 trials found)
- Patent FTO: Clear (2 active, 5 expired)
- Market Potential: High (growing NAFLD market)
- **Overall Score**: ~0.75/1.0

### Test 4: Competitive Analysis

**Purpose**: Test competitive landscape analysis

1. Select **"💬 Strategic Prompt"** tab
2. Enter prompt:
   ```
   What is the competitive landscape for diabetes drugs in US?
   ```
3. Click **"🚀 Analyze Prompt"**
4. Verify:
   - ✅ Intent: "competitive_analysis"
   - ✅ Workflow: IQVIA → Clinical Trials → Patents → Strategic Opportunity
   - ✅ Competition analysis in results
   - ✅ Market size and players identified

### Test 5: 5-Slide Journey Report Generation

**Purpose**: Test PDF report generation with new format

1. After running any prompt-based analysis (use Test 3)
2. Click **"📄 5-Slide Report"**
3. Wait for report generation (~2-3 seconds)
4. Click **"📥 Download Report"**
5. Open the PDF and verify 5 slides:

**Slide 1: Strategic Question & Context**
- ✅ User's original prompt displayed
- ✅ Intent type shown
- ✅ Extracted entities (molecule, disease, geography)
- ✅ Input method indicated

**Slide 2: Agent Orchestration**
- ✅ Workflow stages listed with status (✓/✗)
- ✅ Execution timeline
- ✅ Data availability per agent
- ✅ Total execution time

**Slide 3: Data Synthesis**
- ✅ IQVIA market insights
- ✅ Patent landscape (using live PatentsView API!)
- ✅ Clinical trials overview
- ✅ EXIM trade trends

**Slide 4: Strategic Opportunity**
- ✅ Innovation narrative
- ✅ Feasibility score (for repurposing)
- ✅ Key insights listed
- ✅ Unmet medical needs

**Slide 5: Recommendations & Next Steps**
- ✅ Actionable recommendations (prioritized)
- ✅ Summary
- ✅ Report metadata (timestamp)

### Test 6: NLP Parsing (Rule-based Fallback)

**Purpose**: Test without Gemini API (rule-based parsing)

1. Remove `GEMINI_API_KEY` from `.env` temporarily
2. Restart backend
3. Try prompt: `Analyze metformin for diabetes in India`
4. Verify:
   - ✅ Still parses correctly (rule-based)
   - ✅ Lower confidence score (0.6 vs 0.9)
   - ✅ Entities extracted via keyword matching
   - ✅ Workflow executes successfully

### Test 7: Example Prompts

Quick tests for various intents:

**Market Discovery**:
```
What are unmet needs in oncology?
Find market opportunities in cardiovascular space
Which therapeutic areas have high patient burden but low competition?
```

**Repurposing**:
```
Can aspirin be repurposed for cancer prevention?
Which molecules are good candidates for CNS repurposing?
```

**Molecule Analysis**:
```
Analyze the patent landscape for atorvastatin
What is the market position of aspirin?
```

**Strategic Questions**:
```
Which CNS molecules are suitable for repurposing in geriatrics?
What oncology areas have strong pipeline activity but low generic penetration?
What are the trends in pharmaceutical imports to India?
```

## 🔍 Backend API Testing (Direct)

### Test NLP Parsing Only

```bash
curl -X POST http://localhost:8000/api/prompt/parse-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Which respiratory diseases show low competition in India?"}'
```

**Expected Response**:
```json
{
  "success": true,
  "query_intent": {
    "intent_type": "market_discovery",
    "primary_entity": null,
    "disease_area": "respiratory",
    "geography": "India",
    "workflow_stages": ["iqvia", "clinical_trials", "strategic_opportunity"],
    "confidence": 0.95
  }
}
```

### Test Full Workflow

```bash
curl -X POST http://localhost:8000/api/prompt/analyze-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Is metformin suitable for NAFLD repurposing?",
    "use_gemini": true
  }'
```

### Test Repurposing Workflow (Direct)

```bash
curl -X POST http://localhost:8000/api/prompt/repurposing-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "molecule": "Metformin",
    "new_indication": "NAFLD",
    "geography": "US"
  }'
```

### Get Example Prompts

```bash
curl http://localhost:8000/api/prompt/prompt-examples
```

### Health Check

```bash
curl http://localhost:8000/
```

**Expected**: Service status with all features listed

## 📊 Feature Checklist

### ✅ Core Requirements Met

- [x] **Free-text prompt input** - Natural language queries supported
- [x] **NLP parsing** - Gemini API + rule-based fallback
- [x] **Multi-stage workflows** - 5 different workflow types
- [x] **Repurposing evaluation** - Complete 6-stage pipeline
- [x] **Strategic synthesis** - Strategic Opportunity Agent
- [x] **5-slide journey report** - PDF with full workflow narrative
- [x] **Live API integration** - PatentsView API for real patent data
- [x] **Mock APIs** - IQVIA, Clinical Trials, EXIM (mock data)
- [x] **Unmet needs identification** - Automated gap analysis
- [x] **Innovation narratives** - Compelling stories generated
- [x] **Feasibility scoring** - 0.0-1.0 scale for repurposing
- [x] **Backward compatibility** - Legacy structured input still works

### ✅ Workflow Types Implemented

1. **molecule_analysis** - Analyze specific drug
2. **market_discovery** - Find market opportunities
3. **repurposing** - Evaluate drug repurposing (6 stages)
4. **competitive_analysis** - Competitive landscape
5. **strategic_question** - General strategic insights

### ✅ Agent Coverage

- **IQVIA Agent** - Market data (mock)
- **Patent Agent** - Live PatentsView API 🔴 LIVE
- **Clinical Trials Agent** - Trial landscape (mock)
- **EXIM Agent** - Trade data (mock)
- **Web Intelligence Agent** - Web research
- **Strategic Opportunity Agent** - Synthesis & insights
- **NLP Agent** - Prompt parsing

## 🐛 Common Issues & Solutions

### Issue 1: Gemini API Error

**Error**: `Failed to analyze prompt: Gemini parsing failed`

**Solution**: 
- Check `GEMINI_API_KEY` in `.env`
- System will fall back to rule-based parsing automatically
- Rule-based works but with lower confidence

### Issue 2: PatentsView API Not Working

**Error**: Patents show "No data"

**Solution**:
- Check `PATENTSVIEW_API_KEY` in `.env`
- Get API key from: https://search.patentsview.org/
- System falls back to mock data if API unavailable

### Issue 3: Frontend Not Showing Workflow Results

**Error**: Tab shows "No data"

**Solution**:
- Check browser console for errors
- Verify API endpoint: `http://localhost:8000/api/prompt/analyze-prompt`
- Check CORS settings in `backend/app/main.py`

### Issue 4: Report Generation Fails

**Error**: "Failed to generate journey report"

**Solution**:
- Check `backend/reports/` directory exists
- Verify reportlab installed: `pip install reportlab`
- Check file permissions

## 🎯 Success Criteria

Your implementation is successful if:

1. ✅ You can input free-text prompts
2. ✅ System correctly identifies intent
3. ✅ Multi-agent workflow executes
4. ✅ Strategic insights are generated
5. ✅ 5-slide PDF report downloads
6. ✅ Patent data comes from live PatentsView API
7. ✅ Feasibility score calculates for repurposing
8. ✅ Recommendations are actionable
9. ✅ Legacy structured input still works
10. ✅ All workflows complete in <15 seconds

## 📸 Visual Verification

### Frontend Should Show:

**Structured Input Mode**:
- 3 input fields (Molecule, Disease, Region)
- "Run Agent" button
- Classic dashboard view

**Prompt Input Mode**:
- Large text area for prompt
- Example prompt buttons
- "🚀 Analyze Prompt" button
- "📄 5-Slide Report" button

**Workflow Results View**:
- Query intent card (violet background)
- Execution log with ✓/✗ indicators
- Strategic opportunity card (amber background)
- Feasibility score with colored progress bar
- Key insights list
- Recommendations (numbered boxes)
- Unmet needs section

## 🔬 Advanced Testing

### Test Multi-Entity Extraction

```
Prompt: "Compare metformin and aspirin for cardiovascular disease in Europe"
```

Expected:
- Primary entity: metformin (or aspirin)
- Disease: cardiovascular
- Geography: Europe
- Intent: competitive_analysis

### Test Complex Workflow

```
Prompt: "Identify generic opportunities in oncology with patent expiries in India and low trial activity"
```

Expected:
- Intent: strategic_question or market_discovery
- Multiple workflow stages
- Complex synthesis

### Test Error Handling

1. Empty prompt → Button disabled
2. Invalid molecule name → Graceful handling
3. API timeout → Fallback to mock data

## 📝 Report Validation

When reviewing the 5-slide PDF:

**Check Slide 1**:
- Original prompt displayed verbatim
- All extracted entities correct
- Intent classification reasonable

**Check Slide 2**:
- All agents that ran are listed
- Success status accurate
- Execution time realistic (<15s)

**Check Slide 3**:
- Patent data from PatentsView (not mock)
- Market data summarized
- Trial counts reasonable

**Check Slide 4**:
- Innovation story is coherent
- Feasibility score matches workflow
- Insights are specific to the prompt

**Check Slide 5**:
- Recommendations are actionable
- Not generic (tailored to analysis)
- Next steps are clear

## 🎉 Final Verification

Run this complete test sequence:

1. **Structured Input Test** → ✅ Works
2. **Market Discovery Prompt** → ✅ Works
3. **Repurposing Prompt** → ✅ Works + Feasibility score
4. **Generate 5-Slide Report** → ✅ PDF downloads
5. **Check Live Patent Data** → ✅ Real PatentsView data
6. **Verify Workflow Execution** → ✅ All stages complete
7. **Test Rule-Based Fallback** → ✅ Works without Gemini

If all ✅, your implementation is **COMPLETE** and ready for demo! 🚀

---

**Need Help?**
- Check `IMPLEMENTATION_PLAN.md` for architecture details
- See API docs at `http://localhost:8000/docs`
- Review execution logs in terminal
