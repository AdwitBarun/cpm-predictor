# backend/main.py

from fastapi import FastAPI
from cpm_predictor.backend.api.main import router as api_router
from cpm_predictor.backend.models.loader import load_models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CPM Predictor API",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cpm-predictor-production.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup_event():
    # Warm load ML artifacts
    load_models()

app.include_router(api_router, prefix="/api")
