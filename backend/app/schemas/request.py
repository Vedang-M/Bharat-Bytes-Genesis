"""
Request Schemas
Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class WaterStatusRequest(BaseModel):
    """Request for getting water status of a location."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the location")
    state: str = Field(default="Uttar Pradesh", description="State name")
    district: str = Field(..., description="District name")
    block: Optional[str] = Field(None, description="Block/Tehsil name for finer data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 25.4358,
                "longitude": 81.8463,
                "state": "Uttar Pradesh",
                "district": "Prayagraj",
                "block": "Chaka"
            }
        }


class CropViabilityRequest(BaseModel):
    """Request for checking crop viability."""
    crop_id: str = Field(..., description="Crop identifier (e.g., 'sugarcane', 'wheat')")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    state: str = Field(default="Uttar Pradesh")
    district: str = Field(...)
    block: Optional[str] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "sugarcane",
                "latitude": 25.4358,
                "longitude": 81.8463,
                "state": "Uttar Pradesh",
                "district": "Prayagraj",
                "block": "Chaka"
            }
        }


class CropAlternativesRequest(BaseModel):
    """Request for getting alternative crop recommendations."""
    rejected_crop_id: str = Field(..., description="The crop that was rejected")
    available_water_mm: float = Field(..., gt=0, description="Available water in mm")
    max_recommendations: int = Field(default=3, ge=1, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "rejected_crop_id": "sugarcane",
                "available_water_mm": 400,
                "max_recommendations": 3
            }
        }


class BestSowingDateRequest(BaseModel):
    """Request for getting best sowing date."""
    crop_id: str = Field(...)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "wheat",
                "latitude": 25.4358,
                "longitude": 81.8463
            }
        }
