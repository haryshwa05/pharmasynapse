# backend/app/api/mock_data_routes.py
from fastapi import APIRouter
import json, os

router = APIRouter()

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))

def load_json(name: str):
    path = os.path.join(DATA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/clinical/{term}")
def clinical_mock(term: str):
    data = load_json("mock_clinical_trials.json")
    return data.get(term.lower(), data.get("default"))

@router.get("/iqvia/{therapy}")
def iqvia_mock(therapy: str):
    data = load_json("mock_iqvia.json")
    return data.get(therapy.lower(), data.get("default"))
