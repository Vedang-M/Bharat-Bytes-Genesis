"""
Water Status Service
Handles water balance calculations with API data and fallbacks.
"""

import sys
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add ml module to path
ml_path = Path(__file__).parent.parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path.parent))

from .location_service import get_location_details, estimate_state_from_coordinates

# Try to import ML module
try:
    from ml import (
        CROP_DATABASE,
        fetch_weather_forecast,
        fetch_soil_data,
        check_crop_viability,
        get_smart_swap_recommendations,
    )
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ML module: {e}")
    ML_AVAILABLE = False
    CROP_DATABASE = {}


async def fetch_weather_data(lat: float, lon: float) -> dict:
    """
    Fetch weather data from Visual Crossing API.
    Returns processed weather data or fallback values.
    """
    if not ML_AVAILABLE:
        return get_fallback_weather()
    
    try:
        location = f"{lat},{lon}"
        weather = await fetch_weather_forecast(location, days=15)
        return weather
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_fallback_weather()


async def fetch_soil_data_safe(lat: float, lon: float) -> dict:
    """
    Fetch soil data from ISRIC SoilGrids API.
    Returns processed soil data or fallback values.
    """
    if not ML_AVAILABLE:
        return get_fallback_soil()
    
    try:
        soil = await fetch_soil_data(lat, lon)
        return soil
    except Exception as e:
        print(f"Soil API error: {e}")
        return get_fallback_soil()


async def fetch_groundwater_safe(state: str, district: str) -> dict:
    """
    Fetch groundwater data from India WRIS API.
    Returns processed data or fallback values.
    
    Note: India WRIS API often has connectivity issues, so fallback is common.
    """
    try:
        from ml import fetch_groundwater_data
        groundwater = await fetch_groundwater_data(state, district)
        return groundwater
    except Exception as e:
        print(f"Groundwater API error for {district}, {state}: {e}")
        return get_fallback_groundwater(state)


def get_fallback_weather() -> dict:
    """Fallback weather data when API is unavailable."""
    return {
        "daily_data": [],
        "total_rainfall_mm": 150.0,  # Conservative estimate
        "total_et0_mm": 80.0,
        "avg_temp_c": 28.0,
        "forecast_days": 15,
        "data_source": "Fallback (API unavailable)",
        "data_updated_at": datetime.utcnow(),  # Current time as fallback
    }


def get_fallback_soil() -> dict:
    """Fallback soil data when API is unavailable."""
    return {
        "clay_percent": 25.0,
        "sand_percent": 40.0,
        "silt_percent": 35.0,
        "organic_carbon_g_kg": 5.0,
        "soil_ph": 7.5,
        "available_water_capacity_mm_m": 150.0,
        "data_source": "Fallback (API unavailable)",
        "data_updated_at": datetime.utcnow(),  # Current time as fallback
    }


def get_fallback_groundwater(state: str = "Uttar Pradesh") -> dict:
    """
    Fallback groundwater data when API is unavailable.
    Uses conservative estimates based on state.
    """
    # State-wise groundwater estimates (2024 CGWB data average)
    state_estimates = {
        "Punjab": {"depth": 15, "category": "Over-Exploited", "recharge": 150},
        "Haryana": {"depth": 12, "category": "Critical", "recharge": 180},
        "Uttar Pradesh": {"depth": 8, "category": "Semi-Critical", "recharge": 220},
        "Bihar": {"depth": 6, "category": "Safe", "recharge": 280},
        "Madhya Pradesh": {"depth": 10, "category": "Semi-Critical", "recharge": 200},
        "Rajasthan": {"depth": 18, "category": "Over-Exploited", "recharge": 120},
        "Maharashtra": {"depth": 10, "category": "Semi-Critical", "recharge": 200},
        "Gujarat": {"depth": 14, "category": "Critical", "recharge": 160},
    }
    
    estimate = state_estimates.get(state, {"depth": 10, "category": "Semi-Critical", "recharge": 200})
    
    # CGWB 2024 data was published in March 2024
    cgwb_data_date = datetime(2024, 3, 15)
    
    return {
        "category": estimate["category"],
        "avg_depth_m": estimate["depth"],
        "min_depth_m": estimate["depth"] - 2,
        "max_depth_m": estimate["depth"] + 5,
        "recharge_rate_mm": estimate["recharge"],
        "num_readings": 0,
        "state": state,
        "data_source": "CGWB 2024 Assessment",
        "data_updated_at": cgwb_data_date,
    }


def calculate_water_balance(
    weather: dict,
    soil: dict,
    groundwater: dict,
) -> float:
    """
    Calculate available water balance in mm.
    
    Formula:
    Water Balance = (Rainfall + Groundwater Recharge + Soil Water) - (ET0 + Depth Penalty)
    """
    # Extract values
    rainfall_mm = weather.get("total_rainfall_mm", 0) or 0
    et0_mm = weather.get("total_et0_mm", 0) or 0
    soil_awc = soil.get("available_water_capacity_mm_m", 0) or 0
    gw_recharge = groundwater.get("recharge_rate_mm", 0) or 0
    gw_depth = groundwater.get("avg_depth_m", 0) or 0
    
    # Calculate seasonal recharge (divide annual by 4)
    seasonal_recharge = gw_recharge / 4
    
    # Soil water contribution (30% of root zone capacity)
    soil_contribution = soil_awc * 1.5 * 0.3
    
    # ET0 with crop adjustment factor
    adjusted_et0 = et0_mm * 1.2
    
    # Depth penalty (deeper water = harder to access)
    depth_penalty = gw_depth * 2
    
    # Calculate balance
    balance = (
        rainfall_mm +
        seasonal_recharge +
        soil_contribution -
        adjusted_et0 -
        depth_penalty
    )
    
    return max(0, round(balance, 0))


def determine_water_status(water_balance_mm: float) -> str:
    """Determine water status based on available water."""
    if water_balance_mm >= 600:
        return "safe"
    elif water_balance_mm >= 300:
        return "limited"
    else:
        return "critical"


async def get_water_status(
    lat: float,
    lon: float,
    state: Optional[str] = None,
    district: Optional[str] = None,
    block: Optional[str] = None,
) -> dict:
    """
    Get comprehensive water status for a location.
    
    This is the main entry point for the water status API.
    Handles auto-detection of location and graceful fallbacks.
    
    Args:
        lat: Latitude
        lon: Longitude
        state: Optional state name (auto-detected if not provided)
        district: Optional district name (auto-detected if not provided)
        block: Optional block/tehsil name
    
    Returns:
        dict with water balance, status, and all relevant data
    """
    # Step 1: Get location details (auto-detect if needed)
    resolved_state, resolved_district, city = await get_location_details(
        lat, lon, state, district
    )
    
    # Step 2: Fetch all data in parallel
    weather_task = fetch_weather_data(lat, lon)
    soil_task = fetch_soil_data_safe(lat, lon)
    groundwater_task = fetch_groundwater_safe(resolved_state, resolved_district)
    
    weather, soil, groundwater = await asyncio.gather(
        weather_task,
        soil_task,
        groundwater_task,
    )
    
    # Step 3: Calculate water balance
    water_balance_mm = calculate_water_balance(weather, soil, groundwater)
    status = determine_water_status(water_balance_mm)
    
    # Step 4: Calculate solvency
    # Simple solvency calculation based on water balance
    default_crop = CROP_DATABASE.get("wheat", {"water_req_mm": 450, "season_days": 120})
    water_req = default_crop.get("water_req_mm", 450)
    season_days = default_crop.get("season_days", 120)
    
    is_solvent = water_balance_mm >= water_req * 0.7
    solvency_probability = min(1.0, water_balance_mm / water_req)
    
    # Calculate insolvency day
    if is_solvent:
        insolvency_day = None
    else:
        daily_consumption = water_req / season_days
        insolvency_day = int(water_balance_mm / daily_consumption) if daily_consumption > 0 else 0
    
    # Step 5: Prepare response
    return {
        "location": {
            "latitude": lat,
            "longitude": lon,
            "state": resolved_state,
            "district": resolved_district,
            "block": block,
            "city": city,
        },
        "water_balance_mm": water_balance_mm,
        "status": status,
        "crop": {
            "id": "wheat",
            "name": default_crop.get("name_en", "Wheat"),
            "water_required_mm": water_req,
        },
        "solvency": {
            "is_solvent": is_solvent,
            "probability": round(solvency_probability, 2),
            "insolvency_in_days": insolvency_day,
        },
        "safe_to_sow": is_solvent and (insolvency_day is None or insolvency_day > season_days),
        "weather_summary": {
            "forecast_rainfall_mm": weather.get("total_rainfall_mm", 0),
            "forecast_et0_mm": weather.get("total_et0_mm", 0),
            "avg_temp_c": weather.get("avg_temp_c", 0),
        },
        "groundwater_category": groundwater.get("category", "Unknown"),
        "data_sources": {
            "weather": weather.get("data_source", "Unknown"),
            "soil": soil.get("data_source", "Unknown"),
            "groundwater": groundwater.get("data_source", "Unknown"),
        },
        # Timestamp metadata for data freshness
        "data_updated_at": min(
            weather.get("data_updated_at", datetime.utcnow()),
            soil.get("data_updated_at", datetime.utcnow()),
            groundwater.get("data_updated_at", datetime.utcnow()),
        ),
        "forecast_generated_at": datetime.utcnow(),
        "timestamp": datetime.utcnow().isoformat(),
    }


async def check_crop_viability_for_location(
    crop_id: str,
    lat: float,
    lon: float,
    water_available_mm: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
) -> dict:
    """
    Check if a specific crop is viable for a location.
    
    Args:
        crop_id: Crop identifier
        lat: Latitude
        lon: Longitude
        water_available_mm: Optional pre-calculated water (if known)
        state: Optional state name
        district: Optional district name
    
    Returns:
        dict with viability status and recommendations
    """
    # Get water status if not provided
    if water_available_mm is None:
        water_status = await get_water_status(lat, lon, state, district)
        water_available_mm = water_status["water_balance_mm"]
        insolvency_day = water_status["solvency"].get("insolvency_in_days")
    else:
        insolvency_day = None
    
    # Check viability using ML module
    if ML_AVAILABLE:
        viability = check_crop_viability(crop_id, water_available_mm, insolvency_day)
    else:
        # Fallback viability check
        crop = CROP_DATABASE.get(crop_id, {"water_req_mm": 500, "name_en": crop_id.title(), "name_hi": crop_id})
        water_req = crop.get("water_req_mm", 500)
        water_ratio = water_available_mm / water_req if water_req > 0 else 0
        
        if water_ratio >= 1.0:
            recommendation = "suitable"
            is_viable = True
            message = f"{crop.get('name_hi', crop_id)} के लिए पर्याप्त पानी उपलब्ध है।"
            message_en = f"Sufficient water available for {crop.get('name_en', crop_id)}."
        elif water_ratio >= 0.7:
            recommendation = "caution"
            is_viable = True
            message = f"{crop.get('name_hi', crop_id)} उगाया जा सकता है, लेकिन सावधानी बरतें।"
            message_en = f"{crop.get('name_en', crop_id)} can be grown with caution."
        else:
            recommendation = "not-recommended"
            is_viable = False
            message = f"{crop.get('name_hi', crop_id)} के लिए पानी अपर्याप्त है।"
            message_en = f"Insufficient water for {crop.get('name_en', crop_id)}."
        
        viability = {
            "crop_id": crop_id,
            "crop_name": crop.get("name_en", crop_id.title()),
            "crop_name_hi": crop.get("name_hi", crop_id),
            "is_viable": is_viable,
            "recommendation": recommendation,
            "water_required_mm": water_req,
            "water_available_mm": round(water_available_mm, 0),
            "water_ratio": round(water_ratio, 2),
            "water_deficit_mm": max(0, round(water_req - water_available_mm, 0)),
            "season_days": crop.get("season_days", 120),
            "insolvency_warning_days": insolvency_day,
            "message": message,
            "message_en": message_en,
        }
    
    return viability


async def get_alternative_crops(
    rejected_crop_id: str,
    water_available_mm: float,
    max_recommendations: int = 3,
) -> dict:
    """
    Get alternative crop recommendations when a crop is rejected.
    
    Args:
        rejected_crop_id: The crop that was rejected
        water_available_mm: Available water in mm
        max_recommendations: Number of recommendations to return
    
    Returns:
        dict with recommendations ranked by profit-per-drop
    """
    if ML_AVAILABLE:
        recommendations = get_smart_swap_recommendations(
            rejected_crop_id,
            water_available_mm,
            max_recommendations,
        )
    else:
        # Fallback recommendations based on water availability
        recommendations = []
        for crop_id, crop in CROP_DATABASE.items():
            if crop_id == rejected_crop_id:
                continue
            water_req = crop.get("water_req_mm", 500)
            if water_req * 0.7 <= water_available_mm:
                recommendations.append({
                    "crop_id": crop_id,
                    "crop_name": crop.get("name_en", crop_id.title()),
                    "crop_name_hi": crop.get("name_hi", crop_id),
                    "water_required_mm": water_req,
                    "water_need_category": crop.get("water_need_category", "medium"),
                    "profit_per_drop": 0.01,
                    "estimated_profit_inr": 50000,
                    "water_fit_ratio": round(water_available_mm / water_req, 2),
                    "viability_score": round(water_available_mm / water_req, 2),
                    "image": f"/{crop_id}.webp",
                })
        
        # Sort by water fit ratio
        recommendations.sort(key=lambda x: x["water_fit_ratio"], reverse=True)
        recommendations = recommendations[:max_recommendations]
    
    return {
        "rejected_crop": rejected_crop_id,
        "available_water_mm": water_available_mm,
        "recommendations": recommendations,
    }
