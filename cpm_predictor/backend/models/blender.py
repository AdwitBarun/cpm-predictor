from typing import List, Dict, Any, Optional, Union
import numpy as np
from abc import ABC, abstractmethod

from .predictor import BaseCPMPredictor

class ModelBlender(ABC):
    """Abstract base class for model blending/ensembling."""
    
    def __init__(self, models: List[BaseCPMPredictor], weights: Optional[List[float]] = None):
        """Initialize the model blender.
        
        Args:
            models: List of trained predictor models
            weights: Optional list of weights for each model. If None, equal weights are used.
        """
        self.models = models
        self.weights = weights if weights is not None else [1.0/len(models)] * len(models)
        
        if len(self.models) != len(self.weights):
            raise ValueError("Number of models must match number of weights")
    
    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Make a prediction by blending the outputs of multiple models.
        
        Args:
            features: Input features for prediction
            
        Returns:
            Dictionary of blended predictions for each quantile
        """
        pass
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Make batch predictions.
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            List of blended prediction dictionaries
        """
        return [self.predict(features) for features in features_list]


class WeightedAverageBlender(ModelBlender):
    """Blend predictions using a weighted average of model outputs."""
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Make a prediction by taking a weighted average of model outputs.
        
        Args:
            features: Input features for prediction
            
        Returns:
            Dictionary of blended predictions for each quantile
        """
        # Get predictions from all models
        all_preds = [model.predict(features) for model in self.models]
        
        # Initialize result dictionary
        result = {}
        
        # For each quantile, compute weighted average
        for q in all_preds[0].keys():
            weighted_sum = sum(pred[q] * weight for pred, weight in zip(all_preds, self.weights))
            result[q] = weighted_sum / sum(self.weights)
            
        return result


class StackingBlender(ModelBlender):
    """Blend predictions using a meta-model trained on the outputs of base models.
    
    This is a simplified version that would need to be trained on validation data.
    In practice, you would train this on out-of-fold predictions.
    """
    
    def __init__(self, models: List[BaseCPMPredictor], meta_model: Any):
        """Initialize the stacking blender.
        
        Args:
            models: List of base predictor models
            meta_model: Trained meta-model that takes base model predictions as input
        """
        super().__init__(models)
        self.meta_model = meta_model
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Make a prediction using the stacked model approach.
        
        Args:
            features: Input features for prediction
            
        Returns:
            Dictionary of final predictions for each quantile
        """
        # Get predictions from all base models
        base_preds = [model.predict(features) for model in self.models]
        
        # Convert to feature matrix for meta-model
        # This assumes all models predict the same quantiles
        X_meta = []
        for q in base_preds[0].keys():
            X_meta.append([pred[q] for pred in base_preds])
        
        # Reshape for prediction (n_quantiles, n_models) -> (n_quantiles * n_models,)
        X_meta = np.array(X_meta).flatten()
        
        # Get final prediction from meta-model
        # Note: This is a simplified example - in practice, you would need to adapt
        # this to your specific meta-model's input requirements
        final_pred = self.meta_model.predict([X_meta])[0]
        
        # Convert to the expected output format
        # This assumes the meta-model outputs predictions in the same order as quantiles
        return {f"q{int(q*100)}": pred for q, pred in zip(self.models[0].quantiles, final_pred)}


def create_blender(blend_method: str = 'weighted_average', 
                  models: Optional[List[BaseCPMPredictor]] = None,
                  **kwargs) -> ModelBlender:
    """Factory function to create a model blender.
    
    Args:
        blend_method: Method to use for blending ('weighted_average' or 'stacking')
        models: List of base models to blend
        **kwargs: Additional arguments specific to the blending method
            For 'weighted_average': weights (list of floats)
            For 'stacking': meta_model (trained meta-model)
            
    Returns:
        An instance of the specified model blender
    """
    if models is None:
        models = []
    
    if blend_method == 'weighted_average':
        weights = kwargs.get('weights')
        return WeightedAverageBlender(models, weights)
    
    elif blend_method == 'stacking':
        meta_model = kwargs.get('meta_model')
        if meta_model is None:
            raise ValueError("meta_model is required for stacking")
        return StackingBlender(models, meta_model)
    
    else:
        raise ValueError(f"Unknown blend method: {blend_method}")
