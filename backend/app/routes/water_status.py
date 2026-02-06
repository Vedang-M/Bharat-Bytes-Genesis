"""
Water Status Routes
API endpoints for water balance, crop viability, and recommendations.
Optimized for frontend integration with simplified endpoints.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from ..middleware.auth_middleware import require_role

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
    WaterStatusSimpleResponse,
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

@router.get("/water-status", response_model=WaterStatusSimpleResponse)
async def get_water_status_simple(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    role: str = Depends(require_role("farmer"))
):
    """
    Get water status using only lat/lon (simplified for frontend).
    
    Returns a production-ready response with:
    - Location name (human readable)
    - Water level in mm
    - Status: CRITICAL, LOW, MODERATE, or GOOD
    - Timestamp and data source
    
    Requires 'farmer' role or higher.
    """
    from datetime import datetime
    
    try:
        result = await get_water_status(lat, lon)
        
        # Extract water balance - handle NumPy types
        water_level = result.get("water_balance_mm", 0)
        if hasattr(water_level, 'item'):
            water_level = water_level.item()  # Convert numpy scalar
        water_level = float(water_level)
        
        # Map internal status to user-friendly status
        internal_status = result.get("status", "limited")
        if internal_status == "safe" or water_level >= 600:
            status = "GOOD"
        elif internal_status == "limited" or water_level >= 300:
            status = "MODERATE"
        elif water_level >= 100:
            status = "LOW"
        else:
            status = "CRITICAL"
        
        # Build location string
        loc = result.get("location", {})
        location_parts = []
        if loc.get("city"):
            location_parts.append(loc["city"])
        if loc.get("district"):
            location_parts.append(loc["district"])
        if loc.get("state"):
            location_parts.append(loc["state"])
        location_str = ", ".join(location_parts) if location_parts else f"{lat}, {lon}"
        
        # Build data source string
        sources = result.get("data_sources", {})
        source_parts = []
        for key, val in sources.items():
            if val and "Fallback" not in val:
                source_parts.append(key.title())
        data_source = ", ".join(source_parts) if source_parts else "Estimated Data"
        
        return WaterStatusSimpleResponse(
            location=location_str,
            latitude=float(lat),
            longitude=float(lon),
            water_level_mm=water_level,
            status=status,
            last_updated_at=datetime.utcnow(),
            data_source=data_source,
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid coordinates: {str(ve)}")
    except Exception as e:
        # Log the error for debugging
        print(f"Water status error for ({lat}, {lon}): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch water status: {str(e)}")


@router.get("/crop-check/{crop_id}")
async def check_crop_simple(
    crop_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    water_mm: Optional[float] = Query(None, description="Available water in mm (if already known)"),
    role: str = Depends(require_role("farmer"))
):
    """
    Check if a crop is viable (simplified for frontend).
    Requires 'farmer' role or higher.
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
    role: str = Depends(require_role("farmer"))
):
    """
    Get alternative crop recommendations (Smart-Swap).
    Requires 'farmer' role or higher.
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
async def post_water_status(
    request: WaterStatusRequest,
    role: str = Depends(require_role("farmer"))
):
    """
    Get water balance and solvency status for a location (POST version).
    Requires 'farmer' role or higher.
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
async def check_crop_viability_endpoint(
    request: CropViabilityRequest,
    role: str = Depends(require_role("farmer"))
):
    """
    Check if a specific crop is viable for the given location (POST version).
    Requires 'farmer' role or higher.
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
async def get_crop_alternatives_endpoint(
    request: CropAlternativesRequest,
    role: str = Depends(require_role("farmer"))
):
    """
    Get alternative crop recommendations when a crop is rejected.
    Requires 'farmer' role or higher.
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
async def get_best_sowing_date_endpoint(
    request: BestSowingDateRequest,
    role: str = Depends(require_role("farmer"))
):
    """
    Get the best sowing date based on weather forecast.
    Requires 'farmer' role or higher.
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
    List all supported crops. Public endpoint (no auth required for listing).
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
async def get_profit_ranking(role: str = Depends(require_role("farmer"))):
    """
    Get all crops ranked by profit-per-drop.
    Requires 'farmer' role or higher.
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
    role: str = Depends(require_role("sarpanch"))
):
    """
    Get aggregated water statistics for a village/district.
    Requires 'sarpanch' role or higher.
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
    role: str = Depends(require_role("sarpanch"))
):
    """
    Create a notification for village farmers.
    Requires 'sarpanch' role or higher.
    """
    try:
        from ..services.db_service import get_db_service
        db_service = get_db_service()
        
        if db_service.is_available():
            notification_id = await db_service.create_notification(
                from_user_id="sarpanch", 
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
    role: str = Depends(require_role("farmer"))
):
    """
    Get notifications for a location.
    Requires 'farmer' role or higher.
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

