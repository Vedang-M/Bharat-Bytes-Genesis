"""
Sowing Swap Service
Business logic for crop viability assessment and swap recommendations.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


# Data directory path (relative to this file)
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Cache for loaded data
_crop_data_cache: Optional[Dict[str, Any]] = None
_buyer_data_cache: Optional[Dict[str, Any]] = None


def load_crop_dataset() -> Dict[str, Any]:
    """
    Load crop data from JSON file.
    Returns cached data if already loaded, falls back to embedded data on error.
    """
    global _crop_data_cache
    
    if _crop_data_cache is not None:
        return _crop_data_cache
    
    try:
        crop_file = DATA_DIR / "crop_data.json"
        if crop_file.exists():
            with open(crop_file, 'r', encoding='utf-8') as f:
                _crop_data_cache = json.load(f)
                return _crop_data_cache
    except Exception as e:
        print(f"Warning: Could not load crop_data.json: {e}")
    
    # Fallback to embedded data
    _crop_data_cache = CROP_DATABASE_FALLBACK
    return _crop_data_cache


def load_buyer_dataset() -> Dict[str, Any]:
    """
    Load buyer/mandi data from JSON file.
    Returns cached data if already loaded, falls back to embedded data on error.
    """
    global _buyer_data_cache
    
    if _buyer_data_cache is not None:
        return _buyer_data_cache
    
    try:
        buyer_file = DATA_DIR / "buyer_data.json"
        if buyer_file.exists():
            with open(buyer_file, 'r', encoding='utf-8') as f:
                _buyer_data_cache = json.load(f)
                return _buyer_data_cache
    except Exception as e:
        print(f"Warning: Could not load buyer_data.json: {e}")
    
    # Fallback to embedded data
    _buyer_data_cache = BUYER_DATABASE_FALLBACK
    return _buyer_data_cache


# Fallback embedded crop data (used if JSON files not found)
CROP_DATABASE_FALLBACK: Dict[str, Dict[str, Any]] = {
    "sugarcane": {
        "name": "Sugarcane",
        "name_hi": "गन्ना",
        "water_mm": 1800,
        "season": ["kharif"],
        "profit_per_acre": 80000,
        "growth_days": 300,
    },
    "paddy": {
        "name": "Paddy (Rice)",
        "name_hi": "धान",
        "water_mm": 1200,
        "season": ["kharif"],
        "profit_per_acre": 45000,
        "growth_days": 120,
    },
    "wheat": {
        "name": "Wheat",
        "name_hi": "गेहूं",
        "water_mm": 450,
        "season": ["rabi"],
        "profit_per_acre": 40000,
        "growth_days": 120,
    },
    "mustard": {
        "name": "Mustard",
        "name_hi": "सरसों",
        "water_mm": 300,
        "season": ["rabi"],
        "profit_per_acre": 35000,
        "growth_days": 110,
    },
    "chickpea": {
        "name": "Chickpea",
        "name_hi": "चना",
        "water_mm": 350,
        "season": ["rabi"],
        "profit_per_acre": 45000,
        "growth_days": 100,
    },
    "cotton": {
        "name": "Cotton",
        "name_hi": "कपास",
        "water_mm": 700,
        "season": ["kharif"],
        "profit_per_acre": 55000,
        "growth_days": 180,
    },
    "maize": {
        "name": "Maize",
        "name_hi": "मक्का",
        "water_mm": 500,
        "season": ["kharif", "rabi"],
        "profit_per_acre": 35000,
        "growth_days": 100,
    },
    "soybean": {
        "name": "Soybean",
        "name_hi": "सोयाबीन",
        "water_mm": 450,
        "season": ["kharif"],
        "profit_per_acre": 40000,
        "growth_days": 100,
    },
    "groundnut": {
        "name": "Groundnut",
        "name_hi": "मूंगफली",
        "water_mm": 500,
        "season": ["kharif", "zaid"],
        "profit_per_acre": 50000,
        "growth_days": 120,
    },
    "sunflower": {
        "name": "Sunflower",
        "name_hi": "सूरजमुखी",
        "water_mm": 400,
        "season": ["rabi", "zaid"],
        "profit_per_acre": 35000,
        "growth_days": 90,
    },
    "lentil": {
        "name": "Lentil",
        "name_hi": "मसूर",
        "water_mm": 300,
        "season": ["rabi"],
        "profit_per_acre": 42000,
        "growth_days": 110,
    },
    "moong": {
        "name": "Moong (Green Gram)",
        "name_hi": "मूंग",
        "water_mm": 350,
        "season": ["kharif", "zaid"],
        "profit_per_acre": 48000,
        "growth_days": 65,
    },
    "bajra": {
        "name": "Bajra (Pearl Millet)",
        "name_hi": "बाजरा",
        "water_mm": 350,
        "season": ["kharif"],
        "profit_per_acre": 30000,
        "growth_days": 90,
    },
    "jowar": {
        "name": "Jowar (Sorghum)",
        "name_hi": "ज्वार",
        "water_mm": 400,
        "season": ["kharif", "rabi"],
        "profit_per_acre": 28000,
        "growth_days": 100,
    },
    "potato": {
        "name": "Potato",
        "name_hi": "आलू",
        "water_mm": 500,
        "season": ["rabi"],
        "profit_per_acre": 75000,
        "growth_days": 90,
    },
    "onion": {
        "name": "Onion",
        "name_hi": "प्याज",
        "water_mm": 450,
        "season": ["rabi", "kharif"],
        "profit_per_acre": 80000,
        "growth_days": 120,
    },
    "tomato": {
        "name": "Tomato",
        "name_hi": "टमाटर",
        "water_mm": 600,
        "season": ["rabi", "kharif", "zaid"],
        "profit_per_acre": 90000,
        "growth_days": 90,
    },
}

# Fallback mandi/buyer data for market signals (used if JSON files not found)
BUYER_DATABASE_FALLBACK: Dict[str, Dict[str, Any]] = {
    "sugarcane": {
        "mandi_name": "Sugar Mill Direct",
        "price_per_quintal": 350,
        "distance_km": 25,
        "demand_level": "moderate",
    },
    "paddy": {
        "mandi_name": "Government Procurement",
        "price_per_quintal": 2200,
        "distance_km": 15,
        "demand_level": "high",
    },
    "wheat": {
        "mandi_name": "Government Procurement",
        "price_per_quintal": 2275,
        "distance_km": 12,
        "demand_level": "high",
    },
    "mustard": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 5500,
        "distance_km": 18,
        "demand_level": "high",
    },
    "chickpea": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 5200,
        "distance_km": 15,
        "demand_level": "high",
    },
    "cotton": {
        "mandi_name": "Cotton Corporation",
        "price_per_quintal": 6620,
        "distance_km": 30,
        "demand_level": "moderate",
    },
    "maize": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 2090,
        "distance_km": 10,
        "demand_level": "moderate",
    },
    "soybean": {
        "mandi_name": "Oil Mill",
        "price_per_quintal": 4600,
        "distance_km": 20,
        "demand_level": "high",
    },
    "groundnut": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 5850,
        "distance_km": 15,
        "demand_level": "high",
    },
    "sunflower": {
        "mandi_name": "Oil Mill",
        "price_per_quintal": 6400,
        "distance_km": 25,
        "demand_level": "moderate",
    },
    "lentil": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 6200,
        "distance_km": 15,
        "demand_level": "high",
    },
    "moong": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 7755,
        "distance_km": 12,
        "demand_level": "high",
    },
    "bajra": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 2500,
        "distance_km": 10,
        "demand_level": "moderate",
    },
    "jowar": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 3180,
        "distance_km": 10,
        "demand_level": "moderate",
    },
    "potato": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 1500,
        "distance_km": 8,
        "demand_level": "high",
    },
    "onion": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 2000,
        "distance_km": 8,
        "demand_level": "high",
    },
    "tomato": {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 2500,
        "distance_km": 8,
        "demand_level": "high",
    },
}


def get_crop_data(crop_id: str) -> Optional[Dict[str, Any]]:
    """Get crop data by ID (case-insensitive)."""
    crop_db = load_crop_dataset()
    return crop_db.get(crop_id.lower())


def get_all_crops() -> Dict[str, Dict[str, Any]]:
    """Get all crop data."""
    return load_crop_dataset()


def get_buyer_data(crop_id: str) -> Dict[str, Any]:
    """Get buyer/mandi data for a crop."""
    buyer_db = load_buyer_dataset()
    return buyer_db.get(crop_id.lower(), {
        "mandi_name": "Local Mandi",
        "price_per_quintal": 0,
        "distance_km": 20,
        "demand_level": "moderate",
    })


def calculate_risk_level(water_gap: float) -> str:
    """
    Calculate risk level based on water gap.
    
    Args:
        water_gap: Difference between available water and required water (positive = surplus)
    
    Returns:
        Risk level string: SAFE, MODERATE, RISKY, or CRITICAL
    """
    if water_gap >= 100:
        return "SAFE"
    elif water_gap >= 0:
        return "MODERATE"
    elif water_gap >= -200:
        return "RISKY"
    else:
        return "CRITICAL"


def calculate_viability_score(water_gap: float, available_water: float, required_water: float) -> int:
    """
    Calculate viability score (0-100) based on water availability.
    
    Args:
        water_gap: Difference between available and required water
        available_water: Available water in mm
        required_water: Required water in mm
    
    Returns:
        Viability score between 0 and 100
    """
    if required_water <= 0:
        return 100
    
    ratio = available_water / required_water
    
    if ratio >= 1.2:
        return 100
    elif ratio >= 1.0:
        return 80 + int((ratio - 1.0) * 100)
    elif ratio >= 0.8:
        return 60 + int((ratio - 0.8) * 100)
    elif ratio >= 0.5:
        return 30 + int((ratio - 0.5) * 100)
    else:
        return max(0, int(ratio * 60))


def find_alternative_crops(
    current_crop_id: str,
    available_water_mm: float,
    season: str,
    max_alternatives: int = 3
) -> List[Dict[str, Any]]:
    """
    Find alternative crops that fit within available water budget.
    
    Args:
        current_crop_id: ID of the current/planned crop
        available_water_mm: Available water in mm
        season: Growing season (kharif, rabi, zaid)
        max_alternatives: Maximum number of alternatives to return
    
    Returns:
        List of alternative crop recommendations sorted by profit-per-drop
    """
    current_crop = get_crop_data(current_crop_id)
    current_water_mm = current_crop["water_mm"] if current_crop else 0
    
    alternatives = []
    crop_database = load_crop_dataset()
    
    for crop_id, crop_data in crop_database.items():
        # Skip the current crop
        if crop_id.lower() == current_crop_id.lower():
            continue
        
        # Check if crop fits the season
        if season.lower() not in [s.lower() for s in crop_data.get("season", [])]:
            continue
        
        # Check if crop fits within water budget
        if crop_data["water_mm"] > available_water_mm:
            continue
        
        # Calculate profit-per-drop metric
        profit_per_drop = crop_data["profit_per_acre"] / crop_data["water_mm"] if crop_data["water_mm"] > 0 else 0
        
        # Calculate water percentage usage
        water_percentage = (crop_data["water_mm"] / available_water_mm) * 100 if available_water_mm > 0 else 0
        
        # Calculate water savings compared to current crop
        water_saving_percent = 0
        if current_water_mm > 0:
            water_saving_percent = round(((current_water_mm - crop_data["water_mm"]) / current_water_mm) * 100, 1)
        
        # Get buyer/market data
        buyer_data = get_buyer_data(crop_id)
        
        # Generate deterministic reasoning
        reasoning = (
            f"{crop_data['name']} needs {crop_data['water_mm']}mm which is "
            f"within your available {available_water_mm}mm water budget. "
        )
        
        if water_saving_percent > 0:
            reasoning += f"This saves {water_saving_percent}% water compared to {current_crop_id}. "
        
        reasoning += (
            f"It has {buyer_data.get('demand_level', 'moderate')} market demand "
            f"(₹{buyer_data.get('price_per_quintal', 0)}/quintal at {buyer_data.get('mandi_name', 'Local Mandi')}, "
            f"{buyer_data.get('distance_km', 'N/A')}km away)."
        )
        
        alternatives.append({
            "crop_name": crop_data["name"],
            "crop_id": crop_id,
            "water_requirement_mm": crop_data["water_mm"],
            "water_percentage": round(water_percentage, 1),
            "profit_estimate_per_acre": crop_data["profit_per_acre"],
            "profit_per_drop": round(profit_per_drop, 2),
            "water_saving_percent": water_saving_percent,
            "buyer_signal": {
                "mandi_name": buyer_data.get("mandi_name", "Local Mandi"),
                "price_per_quintal": buyer_data.get("price_per_quintal", 0),
                "distance_km": buyer_data.get("distance_km", 0),
                "demand_level": buyer_data.get("demand_level", "moderate"),
            },
            "reasoning": reasoning,
        })
    
    # Sort by profit-per-drop (descending) - best value for water
    alternatives.sort(key=lambda x: x["profit_per_drop"], reverse=True)
    
    # Return top N alternatives
    return alternatives[:max_alternatives]


def assess_sowing_swap(
    current_crop: str,
    available_water_mm: float,
    season: str = "kharif",
    location: Optional[str] = None,
    land_size_acres: Optional[float] = None
) -> Dict[str, Any]:
    """
    Main function to assess crop viability and provide swap recommendations.
    
    Args:
        current_crop: The crop user is planning to grow
        available_water_mm: Available water in mm
        season: Growing season
        location: Optional location string
        land_size_acres: Optional land size
    
    Returns:
        Complete assessment with risk level, alternatives, and explanation
    """
    # Get current crop data
    crop_data = get_crop_data(current_crop)
    
    if not crop_data:
        # Handle unknown crop
        return {
            "current_crop": current_crop,
            "current_crop_water_mm": 0,
            "is_water_safe": False,
            "risk_level": "CRITICAL",
            "water_gap_mm": -available_water_mm,
            "alternatives": find_alternative_crops(current_crop, available_water_mm, season),
            "explanation": f"Unknown crop '{current_crop}'. Please select from available crops.",
            "viability_score": 0,
        }
    
    # Calculate water gap
    required_water_mm = crop_data["water_mm"]
    water_gap = available_water_mm - required_water_mm
    is_safe = water_gap >= 0
    
    # Determine risk level
    risk_level = calculate_risk_level(water_gap)
    
    # Calculate viability score
    viability_score = calculate_viability_score(water_gap, available_water_mm, required_water_mm)
    
    # Find alternatives only if risky
    alternatives = []
    if risk_level in ["RISKY", "CRITICAL"]:
        alternatives = find_alternative_crops(current_crop, available_water_mm, season)
    
    # Generate explanation
    if is_safe:
        explanation = (
            f"{crop_data['name']} requires {required_water_mm}mm of water and you have "
            f"{available_water_mm}mm available. This gives you a surplus of {water_gap}mm. "
            f"This crop is viable for your water budget."
        )
    else:
        explanation = (
            f"{crop_data['name']} requires {required_water_mm}mm but you only have "
            f"{available_water_mm}mm available. You are short by {abs(water_gap)}mm. "
        )
        if alternatives:
            explanation += f"Consider switching to water-efficient alternatives like {alternatives[0]['crop_name']}."
    
    return {
        "current_crop": current_crop,
        "current_crop_water_mm": required_water_mm,
        "is_water_safe": is_safe,
        "risk_level": risk_level,
        "water_gap_mm": water_gap,
        "alternatives": alternatives,
        "explanation": explanation,
        "viability_score": viability_score,
    }
