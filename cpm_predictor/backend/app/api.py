# backend/app/api.py

from fastapi import FastAPI
from cpm_predictor.backend.api.main import app as api_app

app = api_app
