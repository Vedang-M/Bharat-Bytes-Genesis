from pydantic import BaseModel, Field, validator
from typing import Optional


class WaterStatusRequest(BaseModel):
    """Request model for water status endpoint"""
    location: str = Field(..., description="Location name (city, district, or place)", min_length=1)
    
    @validator('location')
    def validate_location(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Location cannot be empty")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "location": "Mumbai"
            }
        }


class CropRecommendationRequest(BaseModel):
    """Request model for crop recommendation endpoint"""
    location: str = Field(..., description="Location name", min_length=1)
    crop_name: Optional[str] = Field(None, description="Specific crop to check (optional)")
    
    @validator('location')
    def validate_location(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Location cannot be empty")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "location": "Pune",
                "crop_name": "Sugarcane"
            }
        }
