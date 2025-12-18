"""
API package for the CPM prediction service.

This package contains the FastAPI routes, schemas, and services
for the CPM prediction API.
"""

from .main import app
from . import schemas, services

__all__ = ['app', 'schemas', 'services']
