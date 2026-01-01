# backend/api/main.py

from fastapi import APIRouter
from cpm_predictor.backend.api.predict import router as predict_router
from cpm_predictor.backend.api.admin import router as admin_router

router = APIRouter()

router.include_router(predict_router)
router.include_router(admin_router)
