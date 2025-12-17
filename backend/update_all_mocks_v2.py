import json
import os
import random
from datetime import datetime, timedelta

DATA_DIR = r"d:\Projects\PharmaSynapse\backend\app\data"

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def generate_mock_patents(molecule):
    patents = []
    statuses = ["active", "expired", "pending"]
    assignees = ["Pfizer", "Merck", "Novartis", "Generic Co A", "Generic Co B", "University X"]
    
    for i in range(25):
        status = random.choice(statuses)
        year = random.randint(2005, 2030)
        patents.append({
            "patent_number": f"US-{random.randint(7000000, 11000000)}",
            "title": f"Method for treating conditions using {molecule} derivative {i}",
            "assignee": random.choice(assignees),
            "jurisdiction": "US",
            "status": status,
            "expiry_date": f"{year}-01-01" if status == "active" else None,
            "fto_risk": "low" if status == "expired" else "high"
        })
    
    overview = {
        "total": len(patents),
        "active_count": sum(1 for p in patents if p["status"] == "active"),
        "expired_count": sum(1 for p in patents if p["status"] == "expired"),
        "pending_count": sum(1 for p in patents if p["status"] == "pending"),
        "earliest_active_expiry": "2026-05-15",
        "has_any_freedom_to_operate": True,
        "as_of_date": datetime.today().strftime("%Y-%m-%d")
    }

    return {
        "molecule": molecule,
        "patents": patents,
        "overview": overview,
        "status_table": [{"status": s, "count": sum(1 for p in patents if p["status"] == s)} for s in statuses],
        "filing_heatmap": {} 
    }

def generate_mock_trials(molecule):
    phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    statuses = ["Recruiting", "Completed", "Active, not recruiting", "Terminated"]
    conditions = ["Diabetes", "Cancer", "Inflammation", "Infection", "Rare Disease"]
    
    trials = []
    for i in range(40):
        trials.append({
            "trial_id": f"NCT{random.randint(10000000, 99999999)}",
            "phase": random.choice(phases),
            "status": random.choice(statuses),
            "condition": f"{random.choice(conditions)} related to {molecule}",
            "sponsor": f"Sponsor {random.choice(['A','B','C','D'])}",
            "repurposing_flag": random.random() > 0.8
        })
        
    return {
        "molecule": molecule,
        "trials": trials,
        "sponsor_profiles": [
            {"sponsor": "Sponsor A", "trials": 12, "focus": "Repurposing"},
            {"sponsor": "Sponsor B", "trials": 8, "focus": "Novel Formulation"}
        ]
    }

def generate_mock_exim(molecule):
    years = [2021, 2022, 2023, 2024]
    countries = ["India", "China", "Germany", "USA", "Brazil", "Japan"]
    
    exports = []
    imports = []
    
    for y in years:
        for c in countries:
            if random.random() > 0.5:
                exports.append({
                    "country": c, "year": y, 
                    "volume_tons": random.randint(100, 1000), 
                    "value_usd_mn": round(random.uniform(10, 50), 1)
                })
            if random.random() > 0.5:
                imports.append({
                    "country": c, "year": y, 
                    "volume_tons": random.randint(50, 500), 
                    "value_usd_mn": round(random.uniform(5, 40), 1)
                })
                
    return {
        "molecule": molecule,
        "exports": exports,
        "imports": imports,
        "insights": [f"Growing export demand from {random.choice(countries)}", "Supply chain stable"],
        "sourcing_insights": ["Consider diversifying API source"]
    }

def generate_mock_internal(molecule):
    return [
        {
            "id": f"doc_{molecule}_1",
            "title": f"{molecule} Strategic Roadmap 2025",
            "type": "strategy_deck",
            "year": 2024,
            "key_takeaways": ["Focus on emerging markets", "Extend patent lifecycle"],
            "comparative_table": [],
            "pdf_url": "#"
        },
        {
            "id": f"doc_{molecule}_2",
            "title": f"Field Insights: {molecule} adoption",
            "type": "field_report",
            "year": 2024,
            "key_takeaways": ["HCPs requesting better dosing", "Payer pushback in EU"],
            "comparative_table": [],
            "pdf_url": "#"
        },
        {
            "id": f"doc_{molecule}_3",
            "title": f"{molecule} Clinical Summary",
            "type": "clinical_summary",
            "year": 2023,
            "key_takeaways": ["Effective in sub-population X"],
            "comparative_table": [],
            "pdf_url": "#"
        }
    ]

# --- MAIN ---

molecules = ["Metformin", "Keytruda", "Humira"]

# 1. Patents
patents_data = load_json("mock_patents.json")
for mol in molecules:
    patents_data[mol.lower()] = generate_mock_patents(mol)
save_json("mock_patents.json", patents_data)
print("Updated mock_patents.json")

# 2. Trials
trials_data = load_json("mock_clinical_trials.json")
for mol in molecules:
    trials_data[mol.lower()] = generate_mock_trials(mol)
save_json("mock_clinical_trials.json", trials_data)
print("Updated mock_clinical_trials.json")

# 3. Exim
exim_data = load_json("mock_exim.json")
for mol in molecules:
    exim_data[mol.lower()] = generate_mock_exim(mol)
save_json("mock_exim.json", exim_data)
print("Updated mock_exim.json")

# 4. Internal
internal_data = load_json("mock_internal_docs.json")
for mol in molecules:
    internal_data[mol.lower()] = generate_mock_internal(mol)
save_json("mock_internal_docs.json", internal_data)
print("Updated mock_internal_docs.json")
