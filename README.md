# PharmaSynapse 🧬

PharmaSynapse is a **full‑stack, agentic AI system for pharmaceutical intelligence and strategic decision‑making**. It is designed to evaluate molecules, therapeutic ideas, and pharma questions end‑to‑end by orchestrating multiple specialized AI agents across **regulatory, clinical, patent, market, trade, and scientific domains**.

This repository contains the **entire working system** — backend intelligence engine, agent orchestration layer, reporting pipeline, and frontend interface — built as a cohesive platform rather than a prototype or demo.

---

## 1. What PharmaSynapse Does

PharmaSynapse answers complex pharma questions such as:

* Is a molecule suitable for **repurposing** into a new indication?
* What are the **regulatory and IP constraints** across regions?
* Does **clinical and scientific evidence** support further development?
* Is there a **real market and trade demand** for the product?

Instead of returning raw search results or generic summaries, PharmaSynapse produces **structured, explainable, decision‑oriented outputs**.

---

## 2. System Philosophy

PharmaSynapse is built on a few core principles:

* **Agentic reasoning over monolithic LLM calls**
* **Domain separation** (each agent owns one expertise)
* **Parallel intelligence gathering** for speed
* **Explainability and traceability** of conclusions
* **Production‑oriented architecture**, not prompt demos

---

## 3. High‑Level Architecture

The system follows a **Master–Worker Agent architecture**.

### Master Agent

The Master Agent acts as the system orchestrator. It:

* Interprets the user’s query or molecule input
* Decomposes it into domain‑specific analytical tasks
* Executes multiple worker agents in parallel
* Aggregates, validates, and synthesizes outputs
* Produces a final unified analysis and recommendation

### Worker Agents

Each Worker Agent is:

* Single‑responsibility
* Independently testable
* Loosely coupled
* Structured‑output driven

---

## 4. Backend Architecture (FastAPI)

The backend is a **FastAPI‑based intelligence service**.

### Entry Point

**`backend/app/main.py`**

* Initializes the FastAPI application
* Configures CORS for frontend communication
* Registers all API routes

### API Layer

Located in **`backend/app/api/`**

* `analysis_routes.py` – molecule and strategy analysis endpoints
* `prompt_routes.py` – flexible natural‑language strategic prompts
* `report_routes.py` – structured report & document generation

These APIs expose the agentic system as a clean service layer.

---

## 5. Agent Layer (Core Intelligence)

Located in **`backend/app/agents/`**

### Master Agent

**`master_agent.py`**

* Central coordination engine
* Uses parallel execution (`ThreadPoolExecutor`) to run agents concurrently
* Normalizes and scores agent outputs
* Produces final structured intelligence

### Key Worker Agents

| Agent                  | Responsibility                                       |
| ---------------------- | ---------------------------------------------------- |
| Regulatory Agent       | Approval pathways, constraints, regional feasibility |
| Clinical Trials Agent  | Trial phases, outcomes, repurposing signals          |
| Patent Agent           | IP status, expiry windows, freedom‑to‑operate        |
| Market Agent           | Demand logic, competition, pricing signals           |
| EXIM Trade Agent       | Import/export data to infer supply–demand gaps       |
| Literature Agent       | Mechanism of action, scientific consensus            |
| Web Intelligence Agent | News, guidelines, policy signals                     |

Each agent returns **structured JSON outputs** instead of free‑text.

---

## 6. Parallel Intelligence Execution

A core design choice is **parallel execution**.

* Agents run simultaneously to reduce latency
* Each agent operates independently
* Failures are isolated and handled gracefully

This mirrors how a real pharma strategy team works — multiple experts in parallel, one final synthesis.

---

## 7. Reporting & Output Generation

PharmaSynapse does not stop at analysis.

### Outputs Include:

* Consolidated analytical summaries
* Risk and opportunity scoring
* Clear go / no‑go signals
* Executive‑level narrative

### Formats:

* JSON (machine‑readable)
* Markdown / text reports
* Auto‑generated PDF / presentation documents

Report generation is handled via a dedicated **Report Agent** pipeline.

---

## 8. Frontend Architecture (Next.js)

The frontend provides a **clean analytical interface** for interacting with the system.

Located in **`frontend/`**:

* React + Next.js
* Tailwind CSS
* Modular components for analysis views and reports

The frontend consumes backend APIs and renders:

* Analysis results
* Structured insights
* Generated reports

---

## 9. Repository Structure

```
PharmaSynapse/
├── backend/
│   └── app/
│       ├── api/
│       ├── agents/
│       ├── services/
│       ├── utils/
│       └── main.py
├── frontend/
│   ├── components/
│   ├── pages/
│   └── styles/
├── data/
│   └── exim/
├── docs/
│   └── prompts.md
├── requirements.txt
└── README.md
```

---

## 10. End‑to‑End Flow

1. User submits a molecule or strategic query
2. Backend API receives the request
3. Master Agent decomposes the task
4. Worker Agents execute in parallel
5. Outputs are normalized and validated
6. Final synthesis is generated
7. Report and presentation artifacts are produced
8. Frontend displays results

---

## 11. Installation & Running

```bash
git clone https://github.com/your-username/PharmaSynapse.git
cd PharmaSynapse

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

---

## 12. Why This System Is Different

* Not a single‑prompt chatbot
* Not hard‑coded rules
* Not static research summaries

PharmaSynapse behaves like a **distributed intelligence system**, combining reasoning, data gathering, validation, and synthesis into one coherent workflow.

---

## 13. Extensibility

The system is intentionally modular:

* New agents can be added without refactoring
* Data sources can be swapped or upgraded
* LLM backends are configurable

---

## 14. Authors

**Haryshwa Ganesh & Indresh**

PharmaSynapse represents an effort to treat AI systems as **thinking infrastructure**, not just interfaces — applying agentic design to real pharmaceutical decision problems.

---

