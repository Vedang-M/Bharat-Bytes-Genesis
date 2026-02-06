from fastapi import APIRouter, HTTPException
from schemas.request import WaterStatusRequest, CropRecommendationRequest
from schemas.response import WaterStatusResponse, CropRecommendationResponse
from services.ml_inference import predict_water_solvency
from services.water_balance import calculate_water_status, estimate_water_availability
from services.crop_advisor import get_crop_recommendation, get_all_crop_recommendations
from datetime import datetime

router = APIRouter()


@router.post("/water-status", response_model=WaterStatusResponse)
async def get_water_status(request: WaterStatusRequest):
    """
    Get water status and solvency prediction for a location
    
    This endpoint uses ML models to predict water availability and
    determine the safety of agricultural activities.
    """
    try:
        # Get ML prediction
        prediction = predict_water_solvency(request.location)
        
        # Calculate derived metrics
        status = calculate_water_status(
            prediction['insolvency_in_days'],
            prediction['safe_to_sow']
        )
        water_availability = estimate_water_availability(
            prediction['insolvency_in_days']
        )
        
        return WaterStatusResponse(
            location=prediction['location'],
            insolvency_in_days=prediction['insolvency_in_days'],
            safe_to_sow=prediction['safe_to_sow'],
            status=status,
            water_availability=water_availability,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing water status request: {str(e)}"
        )


@router.post("/crop-recommendation", response_model=CropRecommendationResponse)
async def get_crop_recommendations(request: CropRecommendationRequest):
    """
    Get crop recommendations based on water availability
    
    Returns recommendations for all crops or a specific crop if specified.
    """
    try:
        # Get ML prediction for water status
        prediction = predict_water_solvency(request.location)
        
        # Calculate water availability
        water_availability = estimate_water_availability(
            prediction['insolvency_in_days']
        )
        
        # Calculate water status
        water_status = calculate_water_status(
            prediction['insolvency_in_days'],
            prediction['safe_to_sow']
        )
        
        # Get crop recommendations
        if request.crop_name:
            # Single crop recommendation
            rec = get_crop_recommendation(
                request.crop_name,
                water_availability,
                prediction['insolvency_in_days']
            )
            if not rec:
                raise HTTPException(
                    status_code=404,
                    detail=f"Crop '{request.crop_name}' not found in database"
                )
            recommendations = [rec]
        else:
            # All crop recommendations
            recommendations = get_all_crop_recommendations(
                water_availability,
                prediction['insolvency_in_days']
            )
        
        return CropRecommendationResponse(
            location=prediction['location'],
            insolvency_in_days=prediction['insolvency_in_days'],
            safe_to_sow=prediction['safe_to_sow'],
            water_status=water_status,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing crop recommendation request: {str(e)}"
        )
