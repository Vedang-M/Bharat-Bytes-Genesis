"""
Sowing Swap Routes
API endpoints for crop viability assessment and swap recommendations.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.sowing_swap import (
    SowingSwapRequest,
    SowingSwapResponse,
    CropAlternative,
    BuyerSignal,
)
from ..services.sowing_swap_service import (
    assess_sowing_swap,
    get_all_crops,
    get_crop_data,
)

router = APIRouter(prefix="/api", tags=["Sowing Swap"])


@router.post("/sowing-swap", response_model=SowingSwapResponse)
async def sowing_swap(request: SowingSwapRequest) -> SowingSwapResponse:
    """
    Assess crop viability and get swap recommendations.
    
    This endpoint evaluates whether a planned crop is viable given the available
    water budget and provides alternative crop recommendations if the risk is high.
    
    **Decision Logic:**
    - Compares crop water requirement against available water
    - Calculates risk level: SAFE, MODERATE, RISKY, or CRITICAL
    - For risky/critical crops, suggests alternatives ranked by profit-per-drop
    
    **Returns:**
    - Viability assessment with risk level
    - Water gap (positive = surplus, negative = deficit)
    - Alternative crop recommendations with market signals
    - Deterministic explanations (no AI-generated text)
    """
    try:
        # Call the assessment service
        result = assess_sowing_swap(
            current_crop=request.current_crop,
            available_water_mm=request.available_water_mm,
            season=request.season,
            location=request.location,
            land_size_acres=request.land_size_acres,
        )
        
        # Convert alternatives to proper schema
        alternatives = []
        for alt in result.get("alternatives", []):
            buyer_signal = BuyerSignal(
                mandi_name=alt["buyer_signal"]["mandi_name"],
                price_per_quintal=alt["buyer_signal"]["price_per_quintal"],
                distance_km=alt["buyer_signal"]["distance_km"],
                demand_level=alt["buyer_signal"]["demand_level"],
            )
            
            alternatives.append(CropAlternative(
                crop_name=alt["crop_name"],
                crop_id=alt["crop_id"],
                water_requirement_mm=alt["water_requirement_mm"],
                water_percentage=alt["water_percentage"],
                profit_estimate_per_acre=alt["profit_estimate_per_acre"],
                profit_per_drop=alt["profit_per_drop"],
                water_saving_percent=alt["water_saving_percent"],
                buyer_signal=buyer_signal,
                reasoning=alt["reasoning"],
            ))
        
        return SowingSwapResponse(
            current_crop=result["current_crop"],
            current_crop_water_mm=result["current_crop_water_mm"],
            is_water_safe=result["is_water_safe"],
            risk_level=result["risk_level"],
            water_gap_mm=result["water_gap_mm"],
            alternatives=alternatives,
            explanation=result["explanation"],
            viability_score=result["viability_score"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error assessing crop viability: {str(e)}"
        )


@router.get("/crops/water-requirements")
async def get_crops_water_requirements():
    """
    Get water requirements for all available crops.
    
    Returns a list of all crops with their water requirements,
    useful for frontend dropdown population and filtering.
    """
    crops = get_all_crops()
    return {
        "crops": [
            {
                "id": crop_id,
                "name": data["name"],
                "name_hi": data.get("name_hi", data["name"]),
                "water_mm": data["water_mm"],
                "season": data["season"],
                "profit_per_acre": data["profit_per_acre"],
            }
            for crop_id, data in crops.items()
        ]
    }


@router.get("/marketplace")
async def get_marketplace(
    available: float,
    season: str = "kharif",
    location: str = "Thane"
):
    """
    Get water-safe crops for the marketplace filtered by available water budget.
    
    Returns crops that fit within the water budget, sorted by profit-per-drop efficiency.
    Each crop includes buyer/market signals for actionable insights.
    
    **Parameters:**
    - available: Available water in mm for the growing season
    - season: Growing season (kharif, rabi, zaid)
    - location: Location for market data (currently informational)
    """
    from ..services.sowing_swap_service import load_crop_dataset, load_buyer_dataset
    
    crops_db = load_crop_dataset()
    buyers_db = load_buyer_dataset()
    
    # Filter water-safe crops for the selected season
    safe_crops = []
    for crop_id, crop_data in crops_db.items():
        # Check water budget
        if crop_data["water_mm"] > available:
            continue
        
        # Check season compatibility
        crop_seasons = crop_data.get("season", [])
        if isinstance(crop_seasons, list):
            if season.lower() not in [s.lower() for s in crop_seasons]:
                continue
        elif crop_seasons.lower() != season.lower():
            continue
        
        # Get buyer data
        buyer_data = buyers_db.get(crop_id, {})
        
        # Calculate profit-per-drop
        water_mm = crop_data["water_mm"]
        profit_per_acre = crop_data.get("profit_per_acre", 0)
        profit_per_drop = profit_per_acre / water_mm if water_mm > 0 else 0
        
        # Calculate water percentage
        water_percentage = (water_mm / available) * 100 if available > 0 else 0
        
        safe_crops.append({
            "id": crop_id,
            "name": crop_data["name"],
            "name_hi": crop_data.get("name_hi", crop_data["name"]),
            "water_mm": water_mm,
            "season": crop_data.get("season", []),
            "profit_per_acre": profit_per_acre,
            "growth_days": crop_data.get("growth_days", 90),
            "profit_per_drop": round(profit_per_drop, 2),
            "water_percentage": round(water_percentage, 1),
            "buyer_signal": {
                "mandi_name": buyer_data.get("mandi_name", "Local Mandi"),
                "price_per_quintal": buyer_data.get("price_per_quintal", 0),
                "distance_km": buyer_data.get("distance_km", 0),
                "demand_level": buyer_data.get("demand_level", "moderate"),
                "contact": buyer_data.get("contact", ""),
            } if buyer_data else None,
        })
    
    # Sort by profit-per-drop (most efficient first)
    safe_crops.sort(key=lambda x: x["profit_per_drop"], reverse=True)
    
    return {
        "available_water_mm": available,
        "season": season,
        "location": location,
        "total_safe_crops": len(safe_crops),
        "crops": safe_crops,
    }

