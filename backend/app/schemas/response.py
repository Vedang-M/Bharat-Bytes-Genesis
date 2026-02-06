from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class WaterStatusResponse(BaseModel):
    """Response model for water status endpoint"""
    location: str = Field(..., description="Location name")
    insolvency_in_days: int = Field(..., description="Days until water insolvency (999 means safe)")
    safe_to_sow: bool = Field(..., description="Whether it's safe to sow crops")
    status: str = Field(..., description="Overall status: safe, limited, or critical")
    water_availability: Optional[int] = Field(None, description="Water availability in mm (estimated)")
    timestamp: str = Field(..., description="Timestamp of the forecast")
    
    class Config:
        schema_extra = {
            "example": {
                "location": "Mumbai",
                "insolvency_in_days": 25,
                "safe_to_sow": True,
                "status": "safe",
                "water_availability": 750,
                "timestamp": "2026-02-06T08:42:18.863Z"
            }
        }


class CropRecommendation(BaseModel):
    """Crop recommendation details"""
    crop_id: str
    crop_name: str
    water_need: str = Field(..., description="high, medium, or low")
    recommendation: str = Field(..., description="suitable, caution, or not-recommended")
    suitability_score: float = Field(..., ge=0, le=100, description="Suitability score (0-100)")
    reasoning: str = Field(..., description="Why this recommendation was made")


class CropRecommendationResponse(BaseModel):
    """Response model for crop recommendation endpoint"""
    location: str
    insolvency_in_days: int
    safe_to_sow: bool
    water_status: str
    recommendations: list[CropRecommendation]
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "location": "Pune",
                "insolvency_in_days": 18,
                "safe_to_sow": True,
                "water_status": "safe",
                "recommendations": [
                    {
                        "crop_id": "wheat",
                        "crop_name": "Wheat",
                        "water_need": "medium",
                        "recommendation": "suitable",
                        "suitability_score": 85.0,
                        "reasoning": "Water availability is sufficient for wheat cultivation"
                    }
                ],
                "timestamp": "2026-02-06T08:42:18.863Z"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    message: str
    version: str
    timestamp: str
