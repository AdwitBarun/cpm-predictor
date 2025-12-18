"""
LLM (Large Language Model) module for the CPM prediction system.

This module provides interfaces to large language models like Gemini for generating
natural language explanations, analyses, and recommendations based on model predictions.
"""

from .gemini_client import GeminiClient
from . import prompts

__all__ = [
    'GeminiClient',
    'prompts'
]
