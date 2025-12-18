import os
import logging
from typing import Dict, Any, Optional, List, Union
import google.generativeai as genai
from google.api_core import retry

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """Initialize the Gemini client.
        
        Args:
            api_key: Google AI API key. If None, will look for GOOGLE_API_KEY environment variable.
            model_name: Name of the Gemini model to use (default: "gemini-pro")
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Either pass it directly or set the GOOGLE_API_KEY environment variable."
            )
            
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Default generation config
        self.generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # Safety settings to block harmful content
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        logger.info(f"Initialized Gemini client with model: {model_name}")
    
    @retry.Retry(
        initial=1.0,
        maximum=60.0,
        multiplier=2.0,
        predicate=retry.if_exception_type(
            Exception,
        ),
    )
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        safety_settings: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate text using the Gemini model.
        
        Args:
            prompt: The input prompt or message
            system_instruction: Optional system instruction to guide the model's behavior
            generation_config: Override default generation config
            safety_settings: Override default safety settings
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Generated text response
        """
        try:
            # Use provided config or defaults
            config = generation_config or self.generation_config
            safety = safety_settings or self.safety_settings
            
            # Create model with system instruction if provided
            model = self.model
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
            
            # Generate response
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(**config),
                safety_settings=safety,
                **kwargs
            )
            
            # Check for safety issues
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                logger.warning(
                    f"Prompt blocked for reason: {response.prompt_feedback.block_reason}"
                )
                return "I'm sorry, I can't process this request due to content safety policies."
            
            if not response.text:
                logger.warning("No text in response")
                return "I'm sorry, I couldn't generate a response. Please try again."
                
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}", exc_info=True)
            raise
    
    async def analyze_campaign_feasibility(
        self,
        campaign_details: Dict[str, Any],
        historical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze campaign feasibility using Gemini.
        
        Args:
            campaign_details: Dictionary containing campaign details
            historical_context: Optional historical data for context
            
        Returns:
            Dictionary containing feasibility analysis
        """
        system_prompt = """
        You are an expert media buyer with deep knowledge of digital advertising campaigns. 
        Analyze the provided campaign details and provide a feasibility assessment.
        Be concise and focus on key factors that would impact campaign success.
        """
        
        prompt = f"""
        Campaign Details:
        {campaign_details}
        
        {f"Historical Context: {historical_context}" if historical_context else ""}
        
        Please analyze this campaign and provide:
        1. Feasibility assessment (High/Medium/Low)
        2. Key strengths and opportunities
        3. Potential risks or challenges
        4. Recommendations for improvement
        """
        
        try:
            response = await self.generate_text(
                prompt=prompt,
                system_instruction=system_prompt
            )
            
            return {
                "feasibility_analysis": response,
                "campaign_id": campaign_details.get("campaign_id", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Error in campaign feasibility analysis: {str(e)}", exc_info=True)
            return {
                "error": f"Failed to analyze campaign: {str(e)}",
                "campaign_id": campaign_details.get("campaign_id", "unknown")
            }
    
    async def explain_prediction(
        self,
        prediction: Dict[str, Any],
        feature_importance: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate a natural language explanation of a prediction.
        
        Args:
            prediction: Dictionary containing prediction details
            feature_importance: Dictionary of feature names to importance scores
            
        Returns:
            Dictionary containing the explanation
        """
        system_prompt = """
        You are an AI assistant that explains machine learning model predictions 
        in clear, non-technical language for business users.
        Focus on the key factors driving the prediction and provide actionable insights.
        """
        
        prompt = f"""
        Please explain this CPM prediction in simple terms:
        
        Prediction: {prediction}
        
        Feature Importance:
        {feature_importance}
        
        Provide a 2-3 sentence explanation that a non-technical user would understand.
        Highlight the most important factors and any recommendations.
        """
        
        try:
            explanation = await self.generate_text(
                prompt=prompt,
                system_instruction=system_prompt
            )
            
            return {
                "explanation": explanation,
                "prediction_id": prediction.get("prediction_id", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}", exc_info=True)
            return {
                "error": f"Failed to generate explanation: {str(e)}",
                "prediction_id": prediction.get("prediction_id", "unknown")
            }
