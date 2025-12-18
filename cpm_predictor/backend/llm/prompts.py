"""
Prompt templates for the CPM Prediction System's LLM integration.

This module contains functions to generate structured prompts for the language model,
ensuring consistent and well-formatted inputs for generating CPM predictions and explanations.
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
import json
from cpm_predictor.backend.llm.utils import (
    decode_tg,
    get_seasonal_factors,
    get_tg_premium_factor,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_gemini_prompt(
    input_data: Dict[str, Any],
    historical_range: Dict[str, float],
    decoded_geo: List[str],
) -> str:
    """
    Generate a structured prompt for the Gemini language model to adjust CPM ranges.
    """
    try:
        # -----------------------------
        # Extract variables explicitly
        # -----------------------------
        tg = input_data.get("TG", "Not specified")
        device = input_data.get("Device", "Not specified")
        inventory_mode = input_data.get("Inventory Mode", "Standard")
        ad_format = input_data.get("Video Ad Format", "Not specified")
        month_range = input_data.get("month_range", "Not specified")

        tg_description = decode_tg(tg)

        historical_low = historical_range.get("p10", 0.0)
        historical_mid = historical_range.get("p50", 0.0)
        historical_high = historical_range.get("p90", 0.0)

        geo = decoded_geo
        current_month = datetime.now().strftime("%B")

        # -----------------------------
        # PROMPT (UNCHANGED)
        # -----------------------------
        prompt = """You are an experienced ad-tech media strategist with deep knowledge of programmatic advertising.

Campaign Details:
- Target Group (TG): {tg} (Decoded: {tg_description})
- Device: {device}
- Inventory Mode: {inventory_mode}
- Video Ad Format: {ad_format}
- Month Range: {month_range} (Current Month: {current_month})
- Geography: {geo}

Historical CPM Range (Based on similar campaigns):
- 10th Percentile (Low): ${historical_low:.2f}
- 50th Percentile (Median): ${historical_mid:.2f}
- 90th Percentile (High): ${historical_high:.2f}

Market Context:
- Current Month: {current_month}
- Seasonal Factors: {seasonal_factors}
- Inventory Pressure: {inventory_pressure}
- TG Premium Factor: {tg_premium_factor}

Additional Considerations:
- TG codes imply gender & age (e.g., F15-44 = Female, 15–44)
- Festivals, elections, and geopolitical events may affect CPM
- Premium demographics and limited inventory typically raise CPM
- Market trends and economic conditions are considered

Task:
1. Analyze the historical CPM range in the context of the provided campaign details
2. Adjust the CPM range considering:
   - Seasonality and current month
   - Target group characteristics
   - Inventory availability
   - Geographic factors
   - Current market conditions
3. Provide a revised CPM range with clear justification
4. Explain what factors are pushing CPM up or down

Return a valid JSON response with the following structure:
{{
    "adjusted_range": {{
        "low": float,
        "mid": float,
        "high": float
    }},
    "explanation": "Detailed explanation of adjustments made...",
    "key_factors": [
        {{"factor": string, "impact": "positive/negative/neutral", "effect": string}}
    ]
}}

Response:""".format(
            tg=tg,
            tg_description=tg_description,
            device=device,
            inventory_mode=inventory_mode,
            ad_format=ad_format,
            month_range=month_range,
            geo=", ".join(geo) if geo else "Global",
            historical_low=historical_low,
            historical_mid=historical_mid,
            historical_high=historical_high,
            current_month=current_month,
            seasonal_factors=get_seasonal_factors(month_range, current_month),
            inventory_pressure="High" if inventory_mode.lower() == "limited" else "Moderate",
            tg_premium_factor=get_tg_premium_factor(tg),
        )

        return prompt

    except Exception as e:
        logger.error(f"Error building Gemini prompt: {str(e)}")
        raise


def decode_tg(tg_code: str) -> str:
    """Decode target group code into human-readable format."""
    if not tg_code or not isinstance(tg_code, str):
        return "Not specified"
        
    try:
        gender_map = {
            'M': 'Male',
            'F': 'Female',
            'A': 'All Genders'
        }
        
        gender = gender_map.get(tg_code[0].upper(), 'All Genders')
        age_range = tg_code[1:] if tg_code[0].upper() in ['M', 'F', 'A'] else tg_code
        
        return f"{gender}, {age_range} years"
    except Exception:
        return tg_code

def get_seasonal_factors(month_range: str, current_month: str) -> str:
    """Get seasonal factors based on month range and current month."""
    # This is a simplified example - in production, you might want to use a more sophisticated approach
    q1_months = ['Jan', 'Feb', 'Mar']
    q2_months = ['Apr', 'May', 'Jun']
    q3_months = ['Jul', 'Aug', 'Sep']
    q4_months = ['Oct', 'Nov', 'Dec']
    
    current_quarter = (
        'Q1' if current_month in q1_months else
        'Q2' if current_month in q2_months else
        'Q3' if current_month in q3_months else 'Q4'
    )
    
    # Add seasonal factors based on quarter
    seasonal_factors = {
        'Q1': "Post-holiday period, typically lower ad spend",
        'Q2': "Spring/early summer, moderate ad spend",
        'Q3': "Summer months, varying ad spend",
        'Q4': "Holiday season, typically highest ad spend"
    }
    
    return seasonal_factors.get(current_quarter, "No significant seasonal factors")

def get_tg_premium_factor(tg_code: str) -> str:
    """Determine if the target group is considered premium."""
    if not tg_code:
        return "Standard"
        
    try:
        # Premium demographics (example)
        premium_tgs = ['F25-34', 'M25-34', 'F35-44', 'M35-44']
        return "Premium" if tg_code in premium_tgs else "Standard"
    except Exception:
        return "Standard"

def parse_gemini_response(response_text: str) -> Dict[str, Any]:
    """
    Parse the response from Gemini into a structured format.
    
    Args:
        response_text: Raw text response from Gemini
        
    Returns:
        Dictionary containing parsed response or error information
    """
    try:
        # Try to extract JSON from the response
        json_str = response_text.strip()
        if '```json' in json_str:
            json_str = json_str.split('```json')[1].split('```')[0].strip()
        
        result = json.loads(json_str)
        
        # Validate the response structure
        if not all(k in result.get('adjusted_range', {}) for k in ['low', 'mid', 'high']):
            raise ValueError("Invalid response format: missing required fields in adjusted_range")
            
        return {
            'success': True,
            'data': result
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        return {
            'success': False,
            'error': f"Invalid JSON response: {str(e)}",
            'raw_response': response_text
        }
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'raw_response': response_text
        }
