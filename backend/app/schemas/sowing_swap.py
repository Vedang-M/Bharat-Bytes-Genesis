"""
Sowing Swap Schemas
Pydantic models for sowing swap request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SowingSwapRequest(BaseModel):
    """Request for checking crop viability and getting swap recommendations."""
    current_crop: str = Field(..., description="The crop user is planning to grow")
    available_water_mm: float = Field(..., gt=0, description="Available water in mm for the growing season")
    season: str = Field(default="kharif", description="Growing season: kharif, rabi, or zaid")
    location: Optional[str] = Field(None, description="Location as 'lat,lon' string")
    land_size_acres: Optional[float] = Field(None, gt=0, description="Land size in acres")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_crop": "sugarcane",
                "available_water_mm": 500,
                "season": "kharif",
                "location": "25.4358,81.8463",
                "land_size_acres": 5.0
            }
        }


class BuyerSignal(BaseModel):
    """Market signal data for a crop."""
    mandi_name: str = Field(default="Local Mandi", description="Name of the nearest mandi")
    price_per_quintal: float = Field(default=0, description="Current price in ₹/quintal")
    distance_km: float = Field(default=0, description="Distance to mandi in km")
    demand_level: str = Field(default="moderate", description="Demand level: high, moderate, or low")


class CropAlternative(BaseModel):
    """Alternative crop recommendation with detailed metrics."""
    crop_name: str = Field(..., description="Name of the alternative crop")
    crop_id: str = Field(..., description="ID of the crop for selection")
    water_requirement_mm: float = Field(..., description="Water requirement in mm")
    water_percentage: float = Field(..., description="Percentage of available water this crop would use")
    profit_estimate_per_acre: float = Field(..., description="Estimated profit in ₹ per acre")
    profit_per_drop: float = Field(..., description="Profit per mm of water (efficiency metric)")
    water_saving_percent: float = Field(default=0, description="Water savings compared to current crop")
    buyer_signal: BuyerSignal = Field(..., description="Market demand and pricing information")
    reasoning: str = Field(..., description="Deterministic explanation of why this crop is recommended")


class SowingSwapResponse(BaseModel):
    """Response with crop viability assessment and alternative recommendations."""
    current_crop: str = Field(..., description="The crop being evaluated")
    current_crop_water_mm: float = Field(..., description="Water requirement of current crop")
    is_water_safe: bool = Field(..., description="Whether current crop is safe given available water")
    risk_level: str = Field(..., description="Risk level: SAFE, MODERATE, RISKY, or CRITICAL")
    water_gap_mm: float = Field(..., description="Water surplus (positive) or deficit (negative)")
    alternatives: List[CropAlternative] = Field(default=[], description="List of alternative crop recommendations")
    explanation: str = Field(..., description="Human-readable explanation of the assessment")
    viability_score: int = Field(..., ge=0, le=100, description="Overall viability score (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_crop": "sugarcane",
                "current_crop_water_mm": 1800,
                "is_water_safe": False,
                "risk_level": "CRITICAL",
                "water_gap_mm": -1300,
                "alternatives": [
                    {
                        "crop_name": "Chickpea",
                        "crop_id": "chickpea",
                        "water_requirement_mm": 350,
                        "water_percentage": 70,
                        "profit_estimate_per_acre": 45000,
                        "profit_per_drop": 128.57,
                        "water_saving_percent": 81,
                        "buyer_signal": {
                            "mandi_name": "Prayagraj Mandi",
                            "price_per_quintal": 5200,
                            "distance_km": 15,
                            "demand_level": "high"
                        },
                        "reasoning": "Chickpea needs only 350mm water, saving 81% compared to sugarcane."
                    }
                ],
                "explanation": "Sugarcane requires 1800mm but you only have 500mm available. You are short by 1300mm.",
                "viability_score": 15
            }
        }
