"""
FastAPI application for the CPM prediction service.

This module defines the API endpoints for the CPM prediction service,
including the main prediction endpoint and related functionality.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from ..models.predictor import predict_range
from ..llm.prompts import build_prompt
from ..llm.gemini_client import call_gemini
from ..models.blender import blend_ranges
from ..features.geo_decoder import decode_geo

# Initialize FastAPI app
app = FastAPI(
    title="CPM Prediction API",
    description="API for predicting CPM ranges with historical and contextual insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict CPM ranges based on input data.
    
    This endpoint takes campaign data and returns predicted CPM ranges
    using both historical data and contextual information from Gemini.
    
    Args:
        data: Dictionary containing campaign features including:
              - Geography Targeting - Include: str, target geography
              - Other campaign parameters
              
    Returns:
        Dictionary containing:
        - historical_range: CPM range based on historical data
        - contextual_range: CPM range from contextual analysis
        - final_range: Blended final CPM range
        - explanation: Natural language explanation of the prediction
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        logger.info(f"Received prediction request: {data}")
        
        # Convert input to DataFrame for processing
        df = pd.DataFrame([data])
        
        # Get historical prediction
        historical = predict_range(df)
        
        # Get geographical context
        geo = decode_geo(data.get("Geography Targeting - Include", ""))
        
        # Build prompt and get contextual analysis
        prompt = build_prompt(data, historical, geo)
        contextual = call_gemini(prompt)
        
        # Blend historical and contextual ranges
        final_range = blend_ranges(historical["historical"], contextual)
        
        # Prepare response
        response = {
            "historical_range": historical,
            "contextual_range": contextual,
            "final_range": final_range,
            "explanation": contextual.get("explanation", "No explanation available")
        }
        
        logger.info("Successfully generated prediction")
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Dictionary indicating the service status.
    """
    return {"status": "healthy"}

# Example usage for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
