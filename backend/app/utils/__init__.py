"""
Utils package init
"""

from .water_utils import (
    normalize_water_to_percentage,
    get_status_from_percentage,
    compress_forecast_data,
    decompress_forecast_data,
    get_compression_ratio,
)

__all__ = [
    "normalize_water_to_percentage",
    "get_status_from_percentage",
    "compress_forecast_data",
    "decompress_forecast_data",
    "get_compression_ratio",
]
