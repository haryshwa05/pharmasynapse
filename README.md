# PharmaSynapse 🧬

**PharmaSynapse** is an **agentic AI system for pharmaceutical intelligence and decision support**, designed to evaluate molecules end-to-end — from scientific rationale and regulatory feasibility to patents, market demand, and global trade signals.

It is built as a **modular, production-oriented platform**, not a demo or chatbot, and is intended to support real-world use cases such as **drug repurposing, value-added generics, portfolio evaluation, and market-entry strategy**.

---

## 📌 Why PharmaSynapse Exists

Modern pharma decisions suffer from three core problems:

* Critical data is **fragmented** across regulatory sites, clinical trial registries, patents, market reports, and trade data
* Analysis is **manual, slow, and expert-dependent**
* Outputs are often **descriptive**, not decision-oriented

PharmaSynapse addresses this by using **agentic AI** to autonomously gather, reason over, and synthesize multi-source intelligence into **clear, defensible recommendations**.

---

## 🧠 System Overview

PharmaSynapse follows a **Master–Worker Agent architecture**.

A central **Master Orchestrator** decomposes a molecule-level question into specialized sub-tasks and coordinates multiple **domain-focused AI agents**. Each agent operates independently, produces structured outputs, and exposes its reasoning and confidence.

The final system output is not raw text, but:

* Structured analytical summaries
* Risk and opportunity signals
* Decision-ready recommendations
* Executive-grade reports and presentations

---

## 🧩 Agent Architecture

### Master Orchestrator Agent

Responsible for:

* Task planning and decomposition
* Routing queries to appropriate worker agents
* Parallel execution and result aggregation
* Cross-agent consistency checks
* Final synthesis and scoring

The Master Agent ensures the system behaves like a **coherent analyst**, not a collection of tools.

---

### Worker Agents

Each Worker Agent is **single-responsibility, independently testable, and replaceable**.

| Agent                         | Core Responsibility                                                         |
| ----------------------------- | --------------------------------------------------------------------------- |
| Regulatory Intelligence Agent | Approval pathways, constraints, regional feasibility (FDA, EMA, CDSCO, WHO) |
| Clinical Evidence Agent       | Trial phases, indications, outcomes, repurposing signals                    |
| Patent & IP Agent             | Patent status, expiry windows, freedom-to-operate assessment                |
| Market Intelligence Agent     | Demand signals, competition, pricing and positioning logic                  |
| EXIM Trade Intelligence Agent | Import/export trends to infer supply–demand gaps                            |
| Scientific Literature Agent   | Mechanism of action, off-label signals, research consensus                  |
| Web Intelligence Agent        | Guidelines, news, policy updates, industry signals                          |

---

## 🔁 End-to-End Workflow

1. **Molecule or compound is provided as input**
2. Master Agent decomposes the evaluation into domain tasks
3. Worker Agents execute in parallel
4. Each agent returns structured insights with confidence scores
5. Master Agent synthesizes findings into unified intelligence
6. Final outputs are generated:

   * Analytical report
   * Executive summary
   * 5-slide strategic presentation

---

## 🏗️ Technical Architecture

### Backend

* **Python 3.11+**
* **FastAPI** for service orchestration
* Custom agent framework (LangChain-compatible)
* Async execution for concurrent agents

### AI / Reasoning Layer

* Configurable LLM backend (OpenAI / open-weight models)
* Tool-calling with structured JSON outputs
* Explicit reasoning traces per agent

### Data & Intelligence Sources

* Regulatory portals
* Clinical trial registries
* Patent databases
* Scientific literature
* Trade (EXIM) datasets
* Open web intelligence

### Frontend

* **React / Next.js**
* Tailwind CSS
* Dashboard-style UI for reports and insights

---

## 📂 Repository Structure

```
PharmaSynapse/
├── backend/
│   ├── agents/
│   │   ├── master_agent.py
│   │   ├── regulatory_agent.py
│   │   ├── clinical_agent.py
│   │   ├── patent_agent.py
│   │   ├── market_agent.py
│   │   └── exim_trade_agent.py
│   ├── services/
│   ├── utils/
│   ├── api.py
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   └── styles/
│
├── data/
│   ├── exim/
│   ├── sample_outputs/
│
├── docs/
│   ├── architecture.md
│   ├── prompts.md
│
├── requirements.txt
└── README.md
```

---

## 📊 System Outputs

PharmaSynapse produces **structured, explainable outputs**, including:

* Regulatory risk level
* Clinical evidence strength
* Patent freedom window
* Market attractiveness score
* Trade-based demand indicators
* Overall feasibility and recommendation

Outputs are available as:

* JSON (machine-readable)
* Markdown / PDF reports
* Auto-generated presentation slides

---

## ⚙️ Installation & Setup

```bash
git clone https://github.com/your-username/PharmaSynapse.git
cd PharmaSynapse

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

uvicorn main:app --reload
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

---

## 🧠 Design Principles

* **Agentic, not monolithic**
* **Explainability over black-box outputs**
* **Domain separation of concerns**
* **Decision-first intelligence**
* **Production-oriented architecture**

---

## 🛣️ Future Extensions

* Internal document RAG
* Portfolio-level molecule comparison
* Feedback-driven agent learning
* Visualization dashboards
* Enterprise authentication and audit logs

---

## 📜 License

MIT License

---

## 👤 Author

**Haryshwa Ganesh**

PharmaSynapse is designed as a **foundational system for AI-driven pharmaceutical intelligence**, extensible across organizations, regions, and therapeutic areas.
