"""Prompt templates for the CPM prediction system.

This module contains all the prompt templates used for generating natural language
explanations, analyses, and other text outputs using the Gemini model.
"""

from typing import Dict, Any, List, Optional

# System prompts
SYSTEM_PROMPTS = {
    "feasibility_analysis": """
    You are an expert media buyer with deep knowledge of digital advertising campaigns.
    Analyze the provided campaign details and provide a feasibility assessment.
    Be concise and focus on key factors that would impact campaign success.
    """,
    
    "prediction_explanation": """
    You are an AI assistant that explains machine learning model predictions
    in clear, non-technical language for business users.
    Focus on the key factors driving the prediction and provide actionable insights.
    """,
    
    "anomaly_detection": """
    You are an expert data analyst specialized in detecting anomalies in advertising data.
    Analyze the provided metrics and identify any unusual patterns or outliers.
    Explain your reasoning in a clear and concise manner.
    """,
    
    "recommendation_engine": """
    You are an expert in digital advertising optimization.
    Based on the provided campaign data and performance metrics,
    provide specific, actionable recommendations to improve campaign performance.
    """
}

def get_feasibility_analysis_prompt(campaign_details: Dict[str, Any], 
                                 historical_context: Optional[Dict[str, Any]] = None) -> str:
    """Generate a prompt for campaign feasibility analysis.
    
    Args:
        campaign_details: Dictionary containing campaign details
        historical_context: Optional historical data for context
        
    Returns:
        Formatted prompt string
    """
    return f"""
    Campaign Details:
    {_format_dict(campaign_details)}
    
    {f"Historical Context: {_format_dict(historical_context)}" if historical_context else ""}
    
    Please analyze this campaign and provide:
    1. Feasibility assessment (High/Medium/Low)
    2. Key strengths and opportunities
    3. Potential risks or challenges
    4. Recommendations for improvement
    """

def get_prediction_explanation_prompt(prediction: Dict[str, Any], 
                                   feature_importance: Dict[str, float]) -> str:
    """Generate a prompt for explaining a prediction.
    
    Args:
        prediction: Dictionary containing prediction details
        feature_importance: Dictionary of feature names to importance scores
        
    Returns:
        Formatted prompt string
    """
    return f"""
    Please explain this CPM prediction in simple terms:
    
    Prediction: {_format_dict(prediction)}
    
    Feature Importance:
    {_format_dict(feature_importance, as_list=True)}
    
    Provide a 2-3 sentence explanation that a non-technical user would understand.
    Highlight the most important factors and any recommendations.
    """

def get_anomaly_detection_prompt(metrics: Dict[str, Any], 
                              baseline: Dict[str, Any]) -> str:
    """Generate a prompt for anomaly detection in campaign metrics.
    
    Args:
        metrics: Current campaign metrics
        baseline: Expected or historical baseline metrics
        
    Returns:
        Formatted prompt string
    """
    return f"""
    Analyze these campaign metrics for anomalies:
    
    Current Metrics:
    {_format_dict(metrics)}
    
    Baseline/Expected Metrics:
    {_format_dict(baseline)}
    
    Please identify any significant anomalies or deviations from expected values.
    For each anomaly, provide:
    1. The metric and its value
    2. How it compares to the baseline
    3. Potential causes
    4. Recommended actions
    """

def get_recommendation_prompt(campaign_data: Dict[str, Any], 
                           performance_metrics: Dict[str, Any]) -> str:
    """Generate a prompt for campaign optimization recommendations.
    
    Args:
        campaign_data: Current campaign settings and parameters
        performance_metrics: Performance metrics for the campaign
        
    Returns:
        Formatted prompt string
    """
    return f"""
    Campaign Data:
    {_format_dict(campaign_data)}
    
    Performance Metrics:
    {_format_dict(performance_metrics)}
    
    Please provide specific, actionable recommendations to improve this campaign's performance.
    Focus on the most impactful changes first and explain the rationale behind each recommendation.
    """

def _format_dict(data: Dict[str, Any], as_list: bool = False) -> str:
    """Helper function to format a dictionary as a readable string.
    
    Args:
        data: Dictionary to format
        as_list: If True, format as a bulleted list
        
    Returns:
        Formatted string representation of the dictionary
    """
    if not data:
        return "No data available"
        
    if as_list:
        return "\n".join(f"- {k}: {v:.4f}" for k, v in data.items() if v != 0)
    
    return "\n".join(f"{k}: {v}" for k, v in data.items())
