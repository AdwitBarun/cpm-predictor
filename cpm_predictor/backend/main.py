from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .app.routes import router

app = FastAPI(
    title="BidVid CPM Predictor",
    version="1.0.0",
    description="Predict CPM feasibility ranges using ML + LLM"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router, prefix="/api")
