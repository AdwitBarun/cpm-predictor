from fastapi import FastAPI
from cpm_predictor.backend.app.routes import router

app = FastAPI(title="CPM Predictor API")

app.include_router(router)
