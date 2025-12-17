import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import routes, mock_data_routes
from app.api import analysis_routes
from app.api import internal_routes
from app.api import report_routes
from app.api import prompt_routes

# Load environment variables from .env if present
load_dotenv()

app = FastAPI(
    title="PharmaSynapse - Strategic Intelligence Platform",
    description="AI-powered pharmaceutical intelligence with prompt-based and structured analysis",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mock_data_routes.router, prefix="/mock", tags=["Mock Data"])
app.include_router(routes.router, prefix="/api", tags=["Legacy Analysis"])
app.include_router(internal_routes.router, prefix="/api", tags=["Internal Knowledge"])
app.include_router(report_routes.router, prefix="/api", tags=["Reports"])
app.include_router(analysis_routes.router, prefix="/api", tags=["Analysis"])
app.include_router(prompt_routes.router, prefix="/api/prompt", tags=["Prompt Analysis"])

@app.get("/", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "PharmaSynapse Strategic Intelligence Platform",
        "version": "2.0.0",
        "features": [
            "Structured molecule analysis",
            "Free-text prompt analysis",
            "Multi-stage repurposing workflows",
            "Strategic opportunity identification",
            "Patent landscape analysis (live PatentsView API)",
            "Clinical trials intelligence",
            "Market and competitive analysis",
            "Import/export trends"
        ],
        "endpoints": {
            "legacy_analysis": "/api/analyze",
            "prompt_analysis": "/api/prompt/analyze-prompt",
            "repurposing": "/api/prompt/repurposing-workflow",
            "prompt_examples": "/api/prompt/prompt-examples",
            "docs": "/docs"
        }
    }
