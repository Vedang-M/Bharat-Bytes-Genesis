from typing import List, Dict


# Crop database with water requirements
CROPS_DATABASE = {
    "sugarcane": {
        "id": "sugarcane",
        "name": "Sugarcane",
        "water_need": "high",
        "min_water_mm": 700,
        "optimal_water_mm": 1000
    },
    "paddy": {
        "id": "paddy",
        "name": "Paddy",
        "water_need": "high",
        "min_water_mm": 650,
        "optimal_water_mm": 950
    },
    "wheat": {
        "id": "wheat",
        "name": "Wheat",
        "water_need": "medium",
        "min_water_mm": 350,
        "optimal_water_mm": 500
    },
    "mustard": {
        "id": "mustard",
        "name": "Mustard",
        "water_need": "low",
        "min_water_mm": 200,
        "optimal_water_mm": 350
    },
    "chickpea": {
        "id": "chickpea",
        "name": "Chickpea",
        "water_need": "low",
        "min_water_mm": 180,
        "optimal_water_mm": 300
    },
    "cotton": {
        "id": "cotton",
        "name": "Cotton",
        "water_need": "medium",
        "min_water_mm": 400,
        "optimal_water_mm": 600
    }
}


def get_crop_recommendation(
    crop_name: str,
    water_availability: int,
    insolvency_in_days: int
) -> Dict:
    """
    Get recommendation for a specific crop
    
    Args:
        crop_name: Name of the crop
        water_availability: Available water in mm
        insolvency_in_days: Days until water insolvency
        
    Returns:
        Dict with crop recommendation details
    """
    crop_key = crop_name.lower()
    
    if crop_key not in CROPS_DATABASE:
        return None
    
    crop = CROPS_DATABASE[crop_key]
    
    # Calculate suitability
    if water_availability >= crop["optimal_water_mm"]:
        recommendation = "suitable"
        suitability_score = 100.0
        reasoning = f"Excellent water availability for {crop['name']} cultivation. Optimal conditions expected."
    elif water_availability >= crop["min_water_mm"]:
        recommendation = "suitable"
        score_range = crop["optimal_water_mm"] - crop["min_water_mm"]
        actual_range = water_availability - crop["min_water_mm"]
        suitability_score = 70.0 + (actual_range / score_range * 30)
        reasoning = f"Good water availability for {crop['name']}. Conditions are favorable with adequate irrigation."
    elif water_availability >= crop["min_water_mm"] * 0.7:
        recommendation = "caution"
        suitability_score = 50.0 + (water_availability / crop["min_water_mm"] * 20)
        reasoning = f"Marginal water availability for {crop['name']}. Consider supplemental irrigation and close monitoring."
    else:
        recommendation = "not-recommended"
        suitability_score = max(0, (water_availability / crop["min_water_mm"] * 50))
        reasoning = f"Insufficient water availability for {crop['name']}. High risk of crop failure. Not recommended."
    
    # Adjust based on insolvency timeline
    if insolvency_in_days <= 10 and recommendation == "suitable":
        recommendation = "caution"
        suitability_score *= 0.8
        reasoning += " Water stress expected in near term."
    
    return {
        "crop_id": crop["id"],
        "crop_name": crop["name"],
        "water_need": crop["water_need"],
        "recommendation": recommendation,
        "suitability_score": round(suitability_score, 1),
        "reasoning": reasoning
    }


def get_all_crop_recommendations(
    water_availability: int,
    insolvency_in_days: int
) -> List[Dict]:
    """
    Get recommendations for all crops
    
    Args:
        water_availability: Available water in mm
        insolvency_in_days: Days until water insolvency
        
    Returns:
        List of crop recommendations sorted by suitability
    """
    recommendations = []
    
    for crop_name in CROPS_DATABASE.values():
        rec = get_crop_recommendation(
            crop_name["name"],
            water_availability,
            insolvency_in_days
        )
        if rec:
            recommendations.append(rec)
    
    # Sort by suitability score (descending)
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    return recommendations
