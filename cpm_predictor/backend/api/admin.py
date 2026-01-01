# backend/api/admin.py

from fastapi import APIRouter, HTTPException
from cpm_predictor.backend.models.historical_store import (
    refresh_from_gsheet_and_save,
    force_refresh,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/refresh-historical-from-gsheet")
def refresh_historical_from_gsheet():
    """
    Download live Google Sheet, save as data_input.csv,
    and refresh in-memory historical cache.
    """
    try:
        refresh_from_gsheet_and_save()

        return {
            "status": "success",
            "message": "Historical data refreshed from Google Sheet and cached",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh from GSheet: {str(e)}",
        )


@router.post("/refresh-historical-from-csv")
def refresh_historical_from_csv():
    """
    Reload historical data from existing CSV (no download).
    """
    try:
        force_refresh()
        return {
            "status": "success",
            "message": "Historical data refreshed from CSV",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
