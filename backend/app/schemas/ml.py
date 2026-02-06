from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class GroundwaterRequest(BaseModel):
    """
    Request parameters for Groundwater Forecasting.
    Can provide lat/lon to fetch soil data, or manually provide soil properties.
    """
    lat: Optional[float] = Field(None, description="Latitude of the location")
    lon: Optional[float] = Field(None, description="Longitude of the location")
    
    # Manual overrides (optional)
    clay_percent: Optional[float] = Field(None, description="Soil Clay Percentage (0-100)")
    sand_percent: Optional[float] = Field(None, description="Soil Sand Percentage (0-100)")
    soil_ph: Optional[float] = Field(None, description="Soil pH Level")
    
    days: int = Field(90, description="Number of days to forecast")

class GroundwaterForecastPoint(BaseModel):
    date: date
    depth_m: float
    trend: str

class GroundwaterResponse(BaseModel):
    location: str
    forecast_days: int
    data_source: str
    forecast: List[GroundwaterForecastPoint]

class ViabilityRequest(BaseModel):
    """
    Raw feature input for Crop Viability Model (XGBoost).
    Allows direct testing of the model logic.
    """
    rainfall_mm: float = Field(..., description="Total seasonal rainfall")
    et0_mm: float = Field(..., description="Total reference evapotranspiration")
    recharge_mm: float = Field(..., description="Groundwater recharge amount")
    soil_awc_mm: float = Field(..., description="Soil Available Water Capacity (mm/m)")
    crop_req_mm: float = Field(..., description="Crop water requirement for season")
    groundwater_depth_m: float = Field(..., description="Current groundwater depth (mbgl)")
    avg_temp_c: float = Field(..., description="Average seasonal temperature")

class ViabilityResponse(BaseModel):
    water_balance_mm: float
    solvency_status: str  # "SOLVENT" or "RISKY"
    solvency_probability: float
    insolvency_in_days: int
    message: str

class YieldResponse(BaseModel):
    crop_id: str
    predicted_yield_quintals: float
    estimated_profit_inr: float
    confidence_score: float = 0.95 # Placeholder for now, could be derived from deviation
