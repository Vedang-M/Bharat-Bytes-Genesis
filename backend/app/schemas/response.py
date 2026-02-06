"""
Response Schemas
Pydantic models for API response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class LocationInfo(BaseModel):
    """Location information."""
    latitude: float
    longitude: float
    state: str
    district: str
    block: Optional[str] = None
    city: Optional[str] = None


class WeatherSummary(BaseModel):
    """Weather forecast summary."""
    forecast_rainfall_mm: float
    forecast_et0_mm: float
    avg_temp_c: float


class CropInfo(BaseModel):
    """Basic crop information."""
    id: str
    name: str
    water_required_mm: int


class SolvencyInfo(BaseModel):
    """Solvency prediction details."""
    is_solvent: bool
    probability: float
    insolvency_in_days: Optional[int] = None


class DataSources(BaseModel):
    """Data source information."""
    weather: Optional[str] = None
    soil: Optional[str] = None
    groundwater: Optional[str] = None


class WaterStatusResponse(BaseModel):
    """Response for water status endpoint."""
    location: LocationInfo
    water_balance_mm: float = Field(..., description="Available water in mm")
    status: str = Field(..., description="safe, limited, or critical")
    crop: CropInfo
    solvency: SolvencyInfo
    safe_to_sow: bool
    weather_summary: WeatherSummary
    groundwater_category: str
    timestamp: str
    data_sources: Optional[DataSources] = None


class WaterStatusSimpleResponse(BaseModel):
    """Simplified response for water status (frontend-friendly)."""
    water_balance_mm: float = Field(..., description="Available water in mm")
    status: str = Field(..., description="safe, limited, or critical")
    location: dict
    solvency: dict
    safe_to_sow: bool
    weather_summary: dict
    groundwater_category: str
    timestamp: str


class CropViabilityResponse(BaseModel):
    """Response for crop viability endpoint."""
    crop_id: str
    crop_name: str
    crop_name_hi: str
    is_viable: bool
    recommendation: str = Field(..., description="suitable, caution, or not-recommended")
    water_required_mm: int
    water_available_mm: float
    water_ratio: float
    water_deficit_mm: float
    season_days: int
    insolvency_warning_days: Optional[int] = None
    message: str
    message_en: str
    best_sowing_date: Optional[dict] = None


class CropRecommendation(BaseModel):
    """Single crop recommendation."""
    crop_id: str
    crop_name: str
    crop_name_hi: str
    water_required_mm: int
    water_need_category: str
    profit_per_drop: float = Field(..., description="INR per liter of water")
    estimated_profit_inr: int = Field(..., description="Estimated profit for 2 acres")
    water_fit_ratio: float
    viability_score: float
    image: str


class CropAlternativesResponse(BaseModel):
    """Response for crop alternatives endpoint."""
    rejected_crop: str
    available_water_mm: float
    recommendations: List[CropRecommendation]
    profit_per_drop_ranking: Optional[List[dict]] = None


class ProfitPerDropItem(BaseModel):
    """Single item in profit-per-drop ranking."""
    rank: int
    crop_id: str
    crop_name: str
    crop_name_hi: str
    water_need_category: str
    water_required_mm: int
    profit_per_drop_inr: float
    estimated_profit_2_acres_inr: int


class BestSowingDateResponse(BaseModel):
    """Response for best sowing date endpoint."""
    crop_id: str
    recommended_date: Optional[dict] = None
    message: Optional[str] = None


class CropListItem(BaseModel):
    """Single crop in crop list."""
    id: str
    name_en: str
    name_hi: str
    water_req_mm: int
    water_need_category: str
    season_days: int
    image: Optional[str] = None


class CropListResponse(BaseModel):
    """Response for crops list endpoint."""
    crops: List[CropListItem]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    ml_available: Optional[bool] = None
