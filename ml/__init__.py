"""
ML Module __init__.py
Exports main functions for use by backend.
ALL DATA IS FETCHED FROM REAL APIs - NO HARDCODED VALUES.
"""

from .config import CROP_DATABASE
from .data_fetchers import (
    fetch_weather_forecast,
    fetch_groundwater_data,
    fetch_soil_data,
    get_village_profile,
)
from .water_wallet_model import (
    WaterWalletModel,
    get_model,
    predict_water_status,
)
from .crop_advisor import (
    check_crop_viability,
    get_smart_swap_recommendations,
    calculate_profit_per_drop,
    calculate_estimated_profit,
    get_profit_per_drop_ranking,
    get_best_sowing_date,
)

__all__ = [
    # Config
    "CROP_DATABASE",
    # Data fetchers
    "fetch_weather_forecast",
    "fetch_groundwater_data",
    "fetch_soil_data",
    "get_village_profile",
    # Model
    "WaterWalletModel",
    "get_model",
    "predict_water_status",
    # Crop advisor
    "check_crop_viability",
    "get_smart_swap_recommendations",
    "calculate_profit_per_drop",
    "calculate_estimated_profit",
    "get_profit_per_drop_ranking",
    "get_best_sowing_date",
]
