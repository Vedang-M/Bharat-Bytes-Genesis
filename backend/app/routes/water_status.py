"""
Water Status Routes
API endpoints for water balance, crop viability, and recommendations.
"""

import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException

# Add ml module to path
ml_path = Path(__file__).parent.parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path.parent))

from ml import (
    predict_water_status,
    get_village_profile,
    check_crop_viability,
    get_smart_swap_recommendations,
    get_profit_per_drop_ranking,
    get_best_sowing_date,
    fetch_weather_forecast,
    get_model,
    CROP_DATABASE,
)

from ..schemas.request import (
    WaterStatusRequest,
    CropViabilityRequest,
    CropAlternativesRequest,
    BestSowingDateRequest,
)
from ..schemas.response import (
    WaterStatusResponse,
    CropViabilityResponse,
    CropAlternativesResponse,
    BestSowingDateResponse,
)

router = APIRouter(prefix="/api", tags=["Water Wallet"])


@router.post("/water-status", response_model=WaterStatusResponse)
async def get_water_status(request: WaterStatusRequest):
    """
    Get water balance and solvency status for a location.
    
    Returns available water, status (safe/limited/critical),
    and predictions for crop solvency.
    """
    try:
        result = await predict_water_status(
            lat=request.latitude,
            lon=request.longitude,
            state=request.state,
            district=request.district,
            block=request.block,
            crop_id="wheat",  # Default crop for general status
        )
        
        return WaterStatusResponse(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude,
                "state": request.state,
                "district": request.district,
                "block": request.block,
            },
            water_balance_mm=result["water_balance_mm"],
            status=result["status"],
            crop=result["crop"],
            solvency=result["solvency"],
            safe_to_sow=result["safe_to_sow"],
            weather_summary=result["weather_summary"],
            groundwater_category=result["groundwater_category"],
            timestamp=result["timestamp"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop-viability", response_model=CropViabilityResponse)
async def check_crop_viability_endpoint(request: CropViabilityRequest):
    """
    Check if a specific crop is viable for the given location.
    
    Returns viability status, recommendation, and best sowing date.
    """
    try:
        # Get water status first
        water_result = await predict_water_status(
            lat=request.latitude,
            lon=request.longitude,
            state=request.state,
            district=request.district,
            block=request.block,
            crop_id=request.crop_id,
        )
        
        # Check viability
        viability = check_crop_viability(
            crop_id=request.crop_id,
            available_water_mm=water_result["water_balance_mm"],
            insolvency_day=water_result["solvency"].get("insolvency_in_days"),
        )
        
        # Get best sowing date
        profile = await get_village_profile(
            lat=request.latitude,
            lon=request.longitude,
            state=request.state,
            district=request.district,
            block=request.block,
        )
        
        weather_data = profile.get("weather", {}).get("daily_data", [])
        best_date = get_best_sowing_date(weather_data, request.crop_id)
        
        return CropViabilityResponse(
            **viability,
            best_sowing_date=best_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop-alternatives", response_model=CropAlternativesResponse)
async def get_crop_alternatives_endpoint(request: CropAlternativesRequest):
    """
    Get alternative crop recommendations when a crop is rejected.
    
    Returns Smart-Swap recommendations ranked by profit-per-drop.
    """
    try:
        recommendations = get_smart_swap_recommendations(
            rejected_crop_id=request.rejected_crop_id,
            available_water_mm=request.available_water_mm,
            max_recommendations=request.max_recommendations,
        )
        
        # Also get full profit-per-drop ranking
        ranking = get_profit_per_drop_ranking()
        
        return CropAlternativesResponse(
            rejected_crop=request.rejected_crop_id,
            available_water_mm=request.available_water_mm,
            recommendations=recommendations,
            profit_per_drop_ranking=ranking,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/best-sowing-date", response_model=BestSowingDateResponse)
async def get_best_sowing_date_endpoint(request: BestSowingDateRequest):
    """
    Get the best sowing date based on weather forecast.
    """
    try:
        weather = await fetch_weather_forecast(
            lat=request.latitude,
            lon=request.longitude,
            days=15,
        )
        
        daily_data = weather.get("daily_data", [])
        best_date = get_best_sowing_date(daily_data, request.crop_id)
        
        return BestSowingDateResponse(
            crop_id=request.crop_id,
            recommended_date=best_date,
            message=best_date.get("message_en") if best_date else "No suitable date found in forecast",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crops")
async def list_crops():
    """List all supported crops with their water requirements."""
    crops = []
    for crop_id, crop_data in CROP_DATABASE.items():
        crops.append({
            "id": crop_id,
            "name_en": crop_data["name_en"],
            "name_hi": crop_data["name_hi"],
            "water_req_mm": crop_data["water_req_mm"],
            "water_need_category": crop_data["water_need_category"],
            "season_days": crop_data["season_days"],
            "image": f"/{crop_id}.webp",
        })
    return {"crops": crops}


@router.get("/profit-ranking")
async def get_profit_ranking():
    """Get all crops ranked by profit-per-drop."""
    ranking = get_profit_per_drop_ranking()
    return {"ranking": ranking}
