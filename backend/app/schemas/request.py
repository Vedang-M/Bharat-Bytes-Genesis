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
    state: Optional[str] = Field(None, description="State name (auto-detected if not provided)")
    district: Optional[str] = Field(None, description="District name (auto-detected if not provided)")
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


class WaterStatusSimpleRequest(BaseModel):
    """Simplified request for getting water status - only lat/lon required."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 25.4358,
                "longitude": 81.8463
            }
        }


class CropViabilityRequest(BaseModel):
    """Request for checking crop viability."""
    crop_id: str = Field(..., description="Crop identifier (e.g., 'sugarcane', 'wheat')")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    state: Optional[str] = Field(None, description="State name (auto-detected if not provided)")
    district: Optional[str] = Field(None, description="District name (auto-detected if not provided)")
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


class CropViabilitySimpleRequest(BaseModel):
    """Simplified request for checking crop viability."""
    crop_id: str = Field(..., description="Crop identifier (e.g., 'sugarcane', 'wheat')")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    water_available_mm: Optional[float] = Field(None, description="Available water in mm (if already known)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "wheat",
                "latitude": 25.4358,
                "longitude": 81.8463
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
