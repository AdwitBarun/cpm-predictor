"""
Geographical Data Decoder for CPM Prediction System

This module provides functionality to decode geographical location IDs into human-readable names
using the geo_master.csv file. It handles loading the mapping data and provides functions to
decode location IDs into their corresponding names.
"""

import os
import pandas as pd
from typing import List, Dict, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GEO_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data',
    'geo_master.csv'
)

# Initialize empty mapping
global geo_map
global is_initialized
is_initialized = False

def _initialize_geo_data() -> None:
    """
    Initialize the geographical data mapping from the CSV file.
    
    This function loads the geo_master.csv file and creates a mapping dictionary
    from location IDs to location names.
    
    Raises:
        FileNotFoundError: If the geo_master.csv file is not found
        Exception: For any other errors during loading
    """
    global geo_map, is_initialized
    
    try:
        logger.info(f"Loading geographical data from {GEO_DATA_PATH}")
        
        # Check if file exists
        if not os.path.exists(GEO_DATA_PATH):
            raise FileNotFoundError(f"Geo data file not found at {GEO_DATA_PATH}")
        
        # Load the CSV file
        df_geo = pd.read_csv(GEO_DATA_PATH)
        
        # Validate required columns
        required_columns = ['criteria_id', 'name']
        missing_columns = [col for col in required_columns if col not in df_geo.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in geo data: {missing_columns}")
        
        # Create the mapping
        geo_map = dict(zip(
            df_geo["criteria_id"].astype(str).str.strip(),
            df_geo["name"].astype(str).str.strip()
        ))
        
        is_initialized = True
        logger.info(f"Successfully loaded {len(geo_map)} geographical mappings")
        
    except Exception as e:
        logger.error(f"Failed to initialize geographical data: {str(e)}")
        geo_map = {}
        is_initialized = False
        raise

def decode_geography(geo_str: Optional[Union[str, float]]) -> List[str]:
    """
    Decode a semicolon-separated string of geographical IDs into location names.
    
    Args:
        geo_str: A string containing semicolon-separated location IDs, or None/NaN
        
    Returns:
        List of location names. If an ID is not found in the mapping, 
        it will be returned as "Unknown(ID)".
        
    Example:
        >>> decode_geography("12345;67890")
        ['New York', 'Los Angeles']
        
        >>> decode_geography("99999")
        ['Unknown(99999)']
        
        >>> decode_geography(None)
        []
    """
    global geo_map, is_initialized
    
    # Initialize if not already done
    if not is_initialized:
        _initialize_geo_data()
    
    # Handle None, NaN, or empty string
    if pd.isna(geo_str) or not str(geo_str).strip():
        return []
    
    try:
        # Split and clean the input string
        ids = [x.strip() for x in str(geo_str).split(";") if x.strip()]
        
        # Map each ID to its corresponding name
        return [
            geo_map.get(i, f"Unknown({i})")
            for i in ids
        ]
        
    except Exception as e:
        logger.error(f"Error decoding geography: {str(e)}")
        return [f"Error: {str(e)}"]

def get_geo_mapping() -> Dict[str, str]:
    """
    Get the complete geographical ID to name mapping.
    
    Returns:
        Dictionary mapping location IDs to names
    """
    global geo_map, is_initialized
    
    if not is_initialized:
        _initialize_geo_data()
        
    return geo_map.copy()

# Initialize on module import
_initialize_geo_data()

# Example usage
if __name__ == "__main__":
    # Example usage
    test_cases = [
        "12345;67890",
        "99999",  # Unknown ID
        "",       # Empty string
        None,     # None
        12345,    # Integer input
        "  12345;  67890  "  # With extra spaces
    ]
    
    for test in test_cases:
        print(f"Input: {test}")
        print(f"Output: {decode_geography(test)}\n")
