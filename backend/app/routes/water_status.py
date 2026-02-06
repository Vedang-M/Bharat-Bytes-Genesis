"""
Water Status Routes
API endpoints for water balance, crop viability, and recommendations.
Optimized for frontend integration with simplified endpoints.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

# Add ml module to path
ml_path = Path(__file__).parent.parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path.parent))

# Import ML module with fallback
try:
    from ml import (
        check_crop_viability,
        get_smart_swap_recommendations,
        get_profit_per_drop_ranking,
        get_best_sowing_date,
        fetch_weather_forecast,
        CROP_DATABASE,
    )
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML module import error: {e}")
    ML_AVAILABLE = False
    CROP_DATABASE = {}

from ..schemas.request import (
    WaterStatusRequest,
    WaterStatusSimpleRequest,
    CropViabilityRequest,
    CropViabilitySimpleRequest,
    CropAlternativesRequest,
    BestSowingDateRequest,
)
from ..schemas.response import (
    WaterStatusResponse,
    CropViabilityResponse,
    CropAlternativesResponse,
    BestSowingDateResponse,
)
from ..services.water_status_service import (
    get_water_status,
    check_crop_viability_for_location,
    get_alternative_crops,
)

router = APIRouter(prefix="/api", tags=["Water Wallet"])


# ==================== SIMPLIFIED ENDPOINTS FOR FRONTEND ====================

@router.get("/water-status")
async def get_water_status_simple(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Get water status using only lat/lon (simplified for frontend).
    
    This is the recommended endpoint for frontend integration.
    State and district are auto-detected from coordinates.
    
    Returns:
        - water_balance_mm: Available water in mm
        - status: "safe", "limited", or "critical"
        - location: Auto-detected location details
        - solvency: Crop solvency prediction
    """
    try:
        result = await get_water_status(lat, lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crop-check/{crop_id}")
async def check_crop_simple(
    crop_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    water_mm: Optional[float] = Query(None, description="Available water in mm (if already known)"),
):
    """
    Check if a crop is viable (simplified for frontend).
    
    This endpoint directly returns crop viability without requiring
    state/district. Perfect for direct frontend integration.
    
    Args:
        crop_id: Crop identifier (e.g., 'wheat', 'sugarcane', 'paddy')
        lat: Latitude
        lon: Longitude
        water_mm: Optional - pass if water availability is already known
    
    Returns:
        - is_viable: boolean
        - recommendation: "suitable", "caution", or "not-recommended"
        - water_required_mm: Water needed for crop
        - water_available_mm: Available water
        - message: Recommendation message in Hindi
        - message_en: Recommendation message in English
    """
    try:
        result = await check_crop_viability_for_location(
            crop_id=crop_id,
            lat=lat,
            lon=lon,
            water_available_mm=water_mm,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/smart-swap/{rejected_crop_id}")
async def get_smart_swap(
    rejected_crop_id: str,
    water_mm: float = Query(..., gt=0, description="Available water in mm"),
    max_results: int = Query(3, ge=1, le=10, description="Number of recommendations"),
):
    """
    Get alternative crop recommendations (Smart-Swap).
    
    When a crop is rejected due to water constraints, this endpoint
    suggests alternative crops that fit the water budget.
    
    Crops are ranked by profit-per-drop (financial efficiency).
    
    Args:
        rejected_crop_id: The crop that was rejected
        water_mm: Available water in mm
        max_results: Number of recommendations to return
    
    Returns:
        - recommendations: List of alternative crops with profit estimates
    """
    try:
        result = await get_alternative_crops(
            rejected_crop_id=rejected_crop_id,
            water_available_mm=water_mm,
            max_recommendations=max_results,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FULL ENDPOINTS (WITH ALL PARAMETERS) ====================

@router.post("/water-status", response_model=WaterStatusResponse)
async def post_water_status(request: WaterStatusRequest):
    """
    Get water balance and solvency status for a location (POST version).
    
    Accepts full location details including state/district.
    Use the GET endpoint for simpler frontend integration.
    """
    try:
        result = await get_water_status(
            lat=request.latitude,
            lon=request.longitude,
            state=request.state,
            district=request.district,
            block=request.block,
        )
        
        return WaterStatusResponse(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude,
                "state": result["location"]["state"],
                "district": result["location"]["district"],
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
    Check if a specific crop is viable for the given location (POST version).
    
    Returns viability status, recommendation, and best sowing date.
    """
    try:
        # Get viability
        viability = await check_crop_viability_for_location(
            crop_id=request.crop_id,
            lat=request.latitude,
            lon=request.longitude,
            state=request.state,
            district=request.district,
        )
        
        # Get best sowing date if ML is available
        best_date = None
        if ML_AVAILABLE:
            try:
                location = f"{request.latitude},{request.longitude}"
                weather = await fetch_weather_forecast(location, days=15)
                daily_data = weather.get("daily_data", [])
                best_date = get_best_sowing_date(daily_data, request.crop_id)
            except Exception as e:
                print(f"Best sowing date error: {e}")
        
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
        result = await get_alternative_crops(
            rejected_crop_id=request.rejected_crop_id,
            water_available_mm=request.available_water_mm,
            max_recommendations=request.max_recommendations,
        )
        
        # Get full profit-per-drop ranking if ML available
        ranking = None
        if ML_AVAILABLE:
            try:
                ranking = get_profit_per_drop_ranking()
            except Exception:
                pass
        
        return CropAlternativesResponse(
            rejected_crop=result["rejected_crop"],
            available_water_mm=result["available_water_mm"],
            recommendations=result["recommendations"],
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
        if not ML_AVAILABLE:
            return BestSowingDateResponse(
                crop_id=request.crop_id,
                recommended_date=None,
                message="Weather forecast unavailable",
            )
        
        location = f"{request.latitude},{request.longitude}"
        weather = await fetch_weather_forecast(location, days=15)
        
        daily_data = weather.get("daily_data", [])
        best_date = get_best_sowing_date(daily_data, request.crop_id)
        
        return BestSowingDateResponse(
            crop_id=request.crop_id,
            recommended_date=best_date,
            message=best_date.get("message_en") if best_date else "No suitable date found in forecast",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILITY ENDPOINTS ====================

@router.get("/crops")
async def list_crops():
    """
    List all supported crops with their water requirements.
    
    Use this to populate crop selection UI in frontend.
    """
    if not ML_AVAILABLE or not CROP_DATABASE:
        # Return default crops if ML module not available
        default_crops = [
            {"id": "sugarcane", "name_en": "Sugarcane", "name_hi": "गन्ना", "water_req_mm": 1800, "water_need_category": "high", "season_days": 365},
            {"id": "paddy", "name_en": "Paddy (Rice)", "name_hi": "धान", "water_req_mm": 1200, "water_need_category": "high", "season_days": 120},
            {"id": "wheat", "name_en": "Wheat", "name_hi": "गेहूं", "water_req_mm": 450, "water_need_category": "medium", "season_days": 120},
            {"id": "mustard", "name_en": "Mustard", "name_hi": "सरसों", "water_req_mm": 250, "water_need_category": "low", "season_days": 110},
            {"id": "chickpea", "name_en": "Chickpea", "name_hi": "चना", "water_req_mm": 300, "water_need_category": "low", "season_days": 100},
            {"id": "cotton", "name_en": "Cotton", "name_hi": "कपास", "water_req_mm": 700, "water_need_category": "medium", "season_days": 180},
        ]
        return {"crops": default_crops}
    
    crops = []
    for crop_id, crop_data in CROP_DATABASE.items():
        crops.append({
            "id": crop_id,
            "name_en": crop_data.get("name_en", crop_id.title()),
            "name_hi": crop_data.get("name_hi", crop_id),
            "water_req_mm": crop_data.get("water_req_mm", 500),
            "water_need_category": crop_data.get("water_need_category", "medium"),
            "season_days": crop_data.get("season_days", 120),
            "image": f"/{crop_id}.webp",
        })
    return {"crops": crops}


@router.get("/profit-ranking")
async def get_profit_ranking():
    """
    Get all crops ranked by profit-per-drop.
    
    This helps farmers understand which crops give best returns
    per liter of water consumed.
    """
    if not ML_AVAILABLE:
        return {"ranking": [], "message": "ML module not available"}
    
    try:
        ranking = get_profit_per_drop_ranking()
        return {"ranking": ranking}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SARPANCH DASHBOARD ENDPOINTS ====================

@router.get("/village-stats")
async def get_village_stats(
    state: str = Query(..., description="State name"),
    district: str = Query(..., description="District name"),
):
    """
    Get aggregated water statistics for a village/district.
    
    Used by Sarpanch dashboard to show village-level water budget.
    """
    try:
        # Import db service
        from ..services.db_service import get_db_service
        db_service = get_db_service()
        
        # Try to get stats from database
        if db_service.is_available():
            stats = await db_service.get_village_stats(state, district)
        else:
            stats = {"total_farmers": 0, "total_farms": 0, "predictions_today": 0}
        
        # Calculate water budget (simplified estimation)
        # In production, aggregate from actual farm data
        total_demand_mm = 4200 + (stats.get("total_farms", 0) * 10)
        total_available_mm = 6800 - (stats.get("predictions_today", 0) * 5)
        utilization = int((total_demand_mm / total_available_mm) * 100) if total_available_mm > 0 else 100
        
        water_status = "SAFE" if utilization < 80 else ("CRITICAL" if utilization > 100 else "LIMITED")
        
        return {
            "state": state,
            "district": district,
            "water_status": water_status,
            "total_demand_mm": total_demand_mm,
            "total_available_mm": total_available_mm,
            "utilization_percentage": utilization,
            "total_farmers": stats.get("total_farmers", 45),
            "total_area_ha": 120 + (stats.get("total_farms", 0) * 2),
            "predictions_today": stats.get("predictions_today", 0),
        }
    except Exception as e:
        # Return default data on error
        return {
            "state": state,
            "district": district,
            "water_status": "SAFE",
            "total_demand_mm": 4200,
            "total_available_mm": 6800,
            "utilization_percentage": 62,
            "total_farmers": 45,
            "total_area_ha": 120,
            "predictions_today": 12,
        }


@router.post("/notifications")
async def create_notification(
    message: str = Query(..., description="Notification message"),
    type: str = Query("info", description="Type: info, warning, critical"),
    state: Optional[str] = Query(None, description="Target state"),
    district: Optional[str] = Query(None, description="Target district"),
):
    """
    Create a notification for village farmers.
    
    Used by Sarpanch to broadcast important updates.
    """
    try:
        from ..services.db_service import get_db_service
        db_service = get_db_service()
        
        if db_service.is_available():
            notification_id = await db_service.create_notification(
                from_user_id="sarpanch",  # Would get from auth in production
                message=message,
                notification_type=type,
                state=state,
                district=district,
            )
            return {
                "success": True,
                "notification_id": notification_id,
                "message": "Notification created successfully",
            }
        else:
            # Mock success for development
            return {
                "success": True,
                "notification_id": f"mock-{datetime.now().timestamp()}",
                "message": "Notification created (demo mode)",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications")
async def get_notifications(
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    limit: int = Query(20, ge=1, le=100, description="Max notifications to return"),
):
    """
    Get notifications for a location.
    """
    try:
        from ..services.db_service import get_db_service
        db_service = get_db_service()
        
        if db_service.is_available():
            notifications = await db_service.get_notifications_for_location(
                state=state,
                district=district,
                limit=limit,
            )
            return {"notifications": notifications}
        else:
            return {"notifications": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

