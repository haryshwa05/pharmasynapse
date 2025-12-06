from fastapi import FastAPI
from app.api import routes, mock_data_routes

app = FastAPI(title="Pharma Agentic AI - Minimal Backend")

app.include_router(mock_data_routes.router, prefix="/mock")
app.include_router(routes.router, prefix="/api")

@app.get("/")
def health():
    return {"status": "ok", "service": "pharm-agentic-ai"}
