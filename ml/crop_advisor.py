"""
Crop Advisor Service
Business logic for crop viability, Smart-Swap recommendations, and Profit-Per-Drop calculations.
"""

from typing import Optional, List
from datetime import datetime, timedelta

from .config import CROP_DATABASE, WATER_STATUS_THRESHOLDS


def check_crop_viability(
    crop_id: str,
    available_water_mm: float,
    insolvency_day: Optional[int] = None
) -> dict:
    """
    Checks if a crop is viable given available water.
    
    Args:
        crop_id: Crop identifier (e.g., "sugarcane", "wheat")
        available_water_mm: Available water in mm
        insolvency_day: Optional predicted day of water exhaustion
    
    Returns:
        dict with viability status and recommendation
    """
    crop = CROP_DATABASE.get(crop_id, CROP_DATABASE.get("wheat"))
    if crop is None:
        return {
            "crop_id": crop_id,
            "is_viable": False,
            "recommendation": "not-recommended",
            "message": f"Unknown crop: {crop_id}",
        }
    
    water_required = crop["water_req_mm"]
    season_days = crop["season_days"]
    
    # Calculate water deficit/surplus
    water_ratio = available_water_mm / water_required if water_required > 0 else 0
    water_deficit = water_required - available_water_mm
    
    # Determine viability and recommendation
    if water_ratio >= 1.0:
        recommendation = "suitable"
        is_viable = True
        message = f"{crop['name_hi']} के लिए पर्याप्त पानी उपलब्ध है। बुवाई की जा सकती है।"
        message_en = f"Sufficient water available for {crop['name_en']}. Safe to sow."
    elif water_ratio >= 0.7:
        recommendation = "caution"
        is_viable = True
        message = f"{crop['name_hi']} उगाया जा सकता है, लेकिन पानी की कमी हो सकती है। सिंचाई की व्यवस्था करें।"
        message_en = f"{crop['name_en']} can be grown but may face water stress. Arrange supplemental irrigation."
    else:
        recommendation = "not-recommended"
        is_viable = False
        deficit_percent = int((1 - water_ratio) * 100)
        message = f"{crop['name_hi']} के लिए {deficit_percent}% पानी की कमी है। कम पानी वाली फसल चुनें।"
        message_en = f"{crop['name_en']} has {deficit_percent}% water deficit. Choose a low-water crop."
    
    # Check insolvency timing
    days_warning = None
    if insolvency_day is not None and insolvency_day < season_days:
        is_viable = False
        recommendation = "not-recommended"
        days_warning = insolvency_day
        message = f"चेतावनी: {insolvency_day} दिनों में पानी खत्म हो जाएगा। फसल पूरी नहीं होगी।"
        message_en = f"Warning: Water will run out in {insolvency_day} days. Crop won't complete cycle."
    
    return {
        "crop_id": crop_id,
        "crop_name": crop["name_en"],
        "crop_name_hi": crop["name_hi"],
        "is_viable": is_viable,
        "recommendation": recommendation,
        "water_required_mm": water_required,
        "water_available_mm": round(available_water_mm, 0),
        "water_ratio": round(water_ratio, 2),
        "water_deficit_mm": max(0, round(water_deficit, 0)),
        "season_days": season_days,
        "insolvency_warning_days": days_warning,
        "message": message,
        "message_en": message_en,
    }


def get_smart_swap_recommendations(
    rejected_crop_id: str,
    available_water_mm: float,
    max_recommendations: int = 3
) -> List[dict]:
    """
    Suggests alternative crops that fit the available water budget.
    Ranks by profit-per-drop to maximize farmer income.
    
    Args:
        rejected_crop_id: The crop that was rejected
        available_water_mm: Available water in mm
        max_recommendations: Number of alternatives to return
    
    Returns:
        List of crop recommendations with profit estimates
    """
    # Access the singleton model for dynamic yield prediction
    # We need to fetch current conditions first - this is a limitation of the current architecture
    # Ideally, get_smart_swap_recommendations should be async and take full profile
    # For now, we will use static profit in this sync function to avoid breaking changes
    # The dynamic profit will be calculated in the API route which has access to context
    
    recommendations = []
    
    for crop_id, crop in CROP_DATABASE.items():
        if crop_id == rejected_crop_id:
            continue
        
        water_required = crop["water_req_mm"]
        
        # Only recommend if crop fits water budget (at least 70%)
        if water_required * 0.7 > available_water_mm:
            continue
        
        # MEANINGFUL CHANGE: We allow the caller to pass yield_map if available
        # But since we are inside a specific function signature, we'll stick to static for sorting
        # specific re-ranking can happen at the API level
        
        profit_per_drop = calculate_profit_per_drop(crop_id)
        total_profit = calculate_estimated_profit(crop_id)
        water_ratio = available_water_mm / water_required
        
        # Calculate viability score (higher is better)
        viability_score = min(water_ratio, 1.5) * profit_per_drop
        
        recommendations.append({
            "crop_id": crop_id,
            "crop_name": crop["name_en"],
            "crop_name_hi": crop["name_hi"],
            "water_required_mm": water_required,
            "water_need_category": crop["water_need_category"],
            "profit_per_drop": profit_per_drop,
            "estimated_profit_inr": total_profit,
            "water_fit_ratio": round(water_ratio, 2),
            "viability_score": round(viability_score, 2),
            "image": f"/{crop_id}.webp",
        })
    
    # Sort by viability score (profit-per-drop * water-fit)
    recommendations.sort(key=lambda x: x["viability_score"], reverse=True)
    
    return recommendations[:max_recommendations]


def calculate_profit_per_drop(crop_id: str) -> float:
    """
    Calculates profit per liter of water consumed (₹/liter).
    This metric helps farmers understand water efficiency in financial terms.
    
    Formula: (Yield × MSP) / (Water Required in liters)
    
    Args:
        crop_id: Crop identifier
    
    Returns:
        Profit in rupees per liter of water
    """
    crop = CROP_DATABASE.get(crop_id)
    if crop is None:
        return 0.0
    
    # Calculate total revenue per acre
    yield_quintals = crop["yield_quintal_per_acre"]
    msp = crop["msp_per_quintal"]
    total_revenue = yield_quintals * msp
    
    # Convert water requirement from mm to liters per acre
    # 1 mm of water on 1 acre = 4046.86 liters
    water_mm = crop["water_req_mm"]
    water_liters = water_mm * 4046.86
    
    # Profit per liter (in rupees)
    profit_per_liter = total_revenue / water_liters if water_liters > 0 else 0
    
    # Convert to paise per liter for readability
    return round(profit_per_liter, 4)


def calculate_estimated_profit(
    crop_id: str, 
    acres: float = 2.0,
    yield_override: Optional[float] = None
) -> int:
    """
    Calculates estimated profit for a given crop.
    
    Args:
        crop_id: Crop identifier
        acres: Land area in acres (default 2 for small farmer)
        yield_override: Optional dynamic yield prediction (if available)
    
    Returns:
        Estimated profit in INR
    """
    crop = CROP_DATABASE.get(crop_id)
    if crop is None:
        return 0
    
    # Use dynamic yield if provided, else fallback to static config
    if yield_override is not None:
        yield_quintals = yield_override * acres
    else:
        yield_quintals = crop["yield_quintal_per_acre"] * acres
        
    revenue = yield_quintals * crop["msp_per_quintal"]
    
    # Rough cost estimation (30-40% of revenue for most crops)
    cost_ratio = 0.35
    profit = revenue * (1 - cost_ratio)
    
    return int(profit)


def get_profit_per_drop_ranking() -> List[dict]:
    """
    Returns all crops ranked by profit-per-drop.
    Useful for showing farmers the financial efficiency of different crops.
    
    Returns:
        List of crops sorted by profit per liter of water
    """
    rankings = []
    
    for crop_id, crop in CROP_DATABASE.items():
        ppd = calculate_profit_per_drop(crop_id)
        profit = calculate_estimated_profit(crop_id)
        
        rankings.append({
            "crop_id": crop_id,
            "crop_name": crop["name_en"],
            "crop_name_hi": crop["name_hi"],
            "water_need_category": crop["water_need_category"],
            "water_required_mm": crop["water_req_mm"],
            "profit_per_drop_inr": ppd,
            "estimated_profit_2_acres_inr": profit,
            "msp_per_quintal": crop["msp_per_quintal"],
            "yield_per_acre": crop["yield_quintal_per_acre"],
        })
    
    # Sort by profit per drop (descending)
    rankings.sort(key=lambda x: x["profit_per_drop_inr"], reverse=True)
    
    # Add rank
    for i, crop in enumerate(rankings):
        crop["rank"] = i + 1
    
    return rankings


def get_best_sowing_date(
    weather_forecast: List[dict],
    crop_id: str,
    min_dry_days: int = 3
) -> Optional[dict]:
    """
    Recommends the best sowing date based on weather forecast.
    Avoids dates with heavy rain (seed washout risk).
    
    Args:
        weather_forecast: List of daily weather data
        crop_id: Crop identifier
        min_dry_days: Minimum consecutive dry days after sowing
    
    Returns:
        dict with recommended date and reasoning, or None if no good date found
    """
    crop = CROP_DATABASE.get(crop_id, CROP_DATABASE.get("wheat"))
    
    best_date = None
    best_score = -1
    
    for i, day in enumerate(weather_forecast):
        if i > len(weather_forecast) - min_dry_days - 1:
            break
        
        # Check rain on sowing day
        precip_mm = day.get("precip_mm", 0)
        
        # Skip if too much rain on sowing day
        if precip_mm > 10:
            continue
        
        # Check next few days for heavy rain
        heavy_rain_ahead = False
        total_rain_week = precip_mm
        
        for j in range(1, min(min_dry_days + 1, len(weather_forecast) - i)):
            next_day_precip = weather_forecast[i + j].get("precip_mm", 0)
            total_rain_week += next_day_precip
            if next_day_precip > 15:  # Heavy rain threshold
                heavy_rain_ahead = True
                break
        
        if heavy_rain_ahead:
            continue
        
        # Score this date (prefer light moisture, not dry)
        # Ideal: 2-5mm rain for seed germination
        if 2 <= precip_mm <= 5:
            score = 10
        elif precip_mm < 2:
            score = 7  # Too dry
        else:
            score = 8 - (precip_mm - 5) * 0.5  # Reduce score for more rain
        
        # Bonus for good temperature
        temp = day.get("temp_c", 25)
        if 20 <= temp <= 30:
            score += 2
        
        if score > best_score:
            best_score = score
            best_date = {
                "date": day.get("date", ""),
                "day_number": i + 1,
                "conditions": day.get("conditions", ""),
                "precip_mm": precip_mm,
                "temp_c": temp,
                "score": round(score, 1),
            }
    
    if best_date:
        # Add recommendation message
        if best_date["precip_mm"] > 0:
            best_date["message"] = f"हल्की बारिश ({best_date['precip_mm']}mm) - बुवाई के लिए अच्छा"
            best_date["message_en"] = f"Light rain ({best_date['precip_mm']}mm) - Good for sowing"
        else:
            best_date["message"] = "सूखा दिन - बुवाई के बाद सिंचाई करें"
            best_date["message_en"] = "Dry day - Irrigate after sowing"
    
    return best_date
