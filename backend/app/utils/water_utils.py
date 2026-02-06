"""
Water Wallet Utility Functions
Backend helper functions for calculations and data transformations.
"""


def normalize_water_to_percentage(water_mm: float) -> float:
    """
    Convert water availability in mm to percentage of optimal water availability.
    500mm or more = 100% (full water wallet)
    
    Args:
        water_mm: Available water in millimeters
    
    Returns:
        Percentage value between 0.0 and 100.0, rounded to 1 decimal place
    
    Examples:
        0mm → 0%
        250mm → 50%
        500mm → 100%
        1000mm → 100% (capped)
    """
    if water_mm <= 0:
        return 0.0
    
    percentage = (water_mm / 500.0) * 100.0
    
    # Cap at 100% and round to 1 decimal place
    return min(round(percentage, 1), 100.0)


def get_status_from_percentage(percentage: float) -> str:
    """
    Get water status category from percentage.
    
    Args:
        percentage: Water availability percentage (0-100)
    
    Returns:
        Status string: CRITICAL, LOW, MODERATE, or GOOD
    """
    if percentage < 20:
        return "CRITICAL"
    elif percentage < 40:
        return "LOW"
    elif percentage < 70:
        return "MODERATE"
    else:
        return "GOOD"


# ==================== COMPRESSION UTILITIES ====================

import gzip
import json
from typing import Any, Union


def compress_forecast_data(forecast_dict: dict) -> bytes:
    """
    Compress forecast data for efficient database storage.
    Reduces storage size by 60-80% for large JSON payloads.
    
    Args:
        forecast_dict: Dictionary containing forecast data
    
    Returns:
        Compressed bytes ready for database storage
    
    Example:
        compressed = compress_forecast_data(large_forecast)
        # Store 'compressed' in database as bytes/blob
    """
    json_str = json.dumps(forecast_dict, separators=(',', ':'))  # Minify JSON
    compressed = gzip.compress(json_str.encode('utf-8'), compresslevel=6)
    return compressed


def decompress_forecast_data(compressed_bytes: bytes) -> dict:
    """
    Decompress forecast data retrieved from database.
    
    Args:
        compressed_bytes: Gzipped bytes from database
    
    Returns:
        Original dictionary with forecast data
    
    Example:
        forecast = decompress_forecast_data(db_row['compressed_data'])
    """
    decompressed = gzip.decompress(compressed_bytes)
    return json.loads(decompressed.decode('utf-8'))


def get_compression_ratio(original: dict) -> float:
    """
    Calculate compression ratio for a given data structure.
    Useful for debugging and optimization.
    
    Args:
        original: Dictionary to measure compression for
    
    Returns:
        Compression ratio (e.g., 0.25 means 75% size reduction)
    """
    original_size = len(json.dumps(original).encode('utf-8'))
    compressed_size = len(compress_forecast_data(original))
    return round(compressed_size / original_size, 3)
