import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import json

from fastapi import HTTPException

from backend.models.predictor import CPMQuantilePredictor
from .schemas import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)

class PredictionService:
    """Service class for handling prediction business logic."""
    
    def __init__(self, model_path: str = None):
        """Initialize the prediction service with a trained model.
        
        Args:
            model_path: Path to the trained model file. If None, will use default path.
        """
        self.model = CPMQuantilePredictor.load(model_path)
        logger.info("Prediction service initialized with model version %s", self.model.version)
    
    async def predict_cpm(self, request: PredictionRequest) -> PredictionResponse:
        """Generate CPM predictions for the given request.
        
        Args:
            request: Prediction request data
            
        Returns:
            PredictionResponse containing the prediction results
            
        Raises:
            HTTPException: If prediction fails
        """
        try:
            # Prepare features for prediction
            features = self._prepare_features(request)
            
            # Generate predictions
            predictions = self.model.predict(features)
            
            # Create response
            return PredictionResponse(
                campaign_id=request.campaign_id,
                prediction_id=f"pred_{uuid.uuid4().hex[:8]}",
                predictions={
                    "q10": round(predictions["q10"], 4),
                    "q50": round(predictions["q50"], 4),
                    "q90": round(predictions["q90"], 4)
                },
                confidence_interval={
                    "lower": round(predictions["q10"] * 0.9, 4),  # Example calculation
                    "upper": round(predictions["q90"] * 1.1, 4)   # Example calculation
                },
                timestamp=datetime.utcnow(),
                model_version=self.model.version
            )
            
        except Exception as e:
            logger.error("Prediction failed: %s", str(e), exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={"error": "Prediction failed", "details": str(e)}
            )
    
    def _prepare_features(self, request: PredictionRequest) -> Dict[str, Any]:
        """Prepare features for model prediction.
        
        Args:
            request: The prediction request
            
        Returns:
            Dictionary of feature names and values
        """
        # This is a simplified example. In practice, you would have more sophisticated
        # feature engineering here based on the request data.
        
        # Add basic features
        features = {
            "placement": request.placement,
            "budget": request.budget,
            "duration_days": request.duration_days,
            "daily_budget": request.budget / request.duration_days if request.duration_days > 0 else 0
        }
        
        # Add targeting features
        if request.targeting:
            features.update({
                f"targeting_{k}": v for k, v in request.targeting.items()
                if isinstance(v, (int, float, str, bool))
            })
            
            # Handle nested targeting features
            if "age_range" in request.targeting and isinstance(request.targeting["age_range"], list):
                features["min_age"] = min(request.targeting["age_range"])
                features["max_age"] = max(request.targeting["age_range"])
        
        return features
    
    def explain_prediction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for a prediction using SHAP values.
        
        Args:
            features: Input features used for prediction
            
        Returns:
            Dictionary containing explanation data
        """
        try:
            if not hasattr(self.model, 'explainer'):
                return {"error": "Model explainer not available"}
                
            shap_values = self.model.explainer.shap_values(features)
            return {
                "shap_values": shap_values.tolist(),
                "expected_value": float(self.model.explainer.expected_value),
                "feature_names": list(features.keys())
            }
        except Exception as e:
            logger.error("Explanation generation failed: %s", str(e))
            return {"error": f"Could not generate explanation: {str(e)}"}

# Singleton instance of the prediction service
prediction_service = PredictionService()
