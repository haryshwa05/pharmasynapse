import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import routes, mock_data_routes
from app.api import analysis_routes
from app.api import internal_routes
from app.api import report_routes

# Load environment variables from .env if present
load_dotenv()

app = FastAPI(title="Pharma Agentic AI - Minimal Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mock_data_routes.router, prefix="/mock")
app.include_router(routes.router, prefix="/api")
app.include_router(internal_routes.router, prefix="/api")
app.include_router(report_routes.router, prefix="/api")

@app.get("/")
def health():
    return {"status": "ok", "service": "pharm-agentic-ai"}
# backend/app/main.py

app.include_router(analysis_routes.router, prefix="/api")
