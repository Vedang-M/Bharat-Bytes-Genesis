"""
Services Package
Contains business logic for Water Wallet API.
"""

from .location_service import (
    reverse_geocode_location,
    get_location_details,
    estimate_state_from_coordinates,
)
from .water_status_service import (
    get_water_status,
    check_crop_viability_for_location,
    get_alternative_crops,
    fetch_weather_data,
    fetch_soil_data_safe,
    fetch_groundwater_safe,
    calculate_water_balance,
    determine_water_status,
)

__all__ = [
    # Location service
    "reverse_geocode_location",
    "get_location_details",
    "estimate_state_from_coordinates",
    # Water status service
    "get_water_status",
    "check_crop_viability_for_location",
    "get_alternative_crops",
    "fetch_weather_data",
    "fetch_soil_data_safe",
    "fetch_groundwater_safe",
    "calculate_water_balance",
    "determine_water_status",
]
