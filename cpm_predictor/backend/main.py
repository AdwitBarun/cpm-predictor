from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app.routes import router   # ✅ relative import

app = FastAPI(
    title="CPM Prediction API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all — relax while dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
