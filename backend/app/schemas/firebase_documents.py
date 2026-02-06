"""
Firebase Document Schemas
Optimized document structures for Firestore storage (<10KB per document).
Only stores aggregated values, not raw data.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LocationData(BaseModel):
    """Compact location representation."""
    lat: float
    lon: float
    city: Optional[str] = None
    state: Optional[str] = None


class WaterStatusSummary(BaseModel):
    """
    Aggregated water status - stores only final values.
    Does NOT store: raw time series, hourly data, full forecasts.
    """
    percentage: float = Field(..., ge=0, le=100, description="Water availability %")
    mm: float = Field(..., description="Available water in mm")
    status: str = Field(..., description="CRITICAL/LOW/MODERATE/GOOD")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ForecastSummary(BaseModel):
    """
    Aggregated forecast summary - stores only statistics.
    Does NOT store: full Prophet output, daily arrays, raw predictions.
    """
    next_week_avg_mm: float = Field(..., description="Average water for next 7 days")
    next_month_avg_mm: Optional[float] = Field(None, description="Average water for next 30 days")
    min_mm: Optional[float] = None
    max_mm: Optional[float] = None
    confidence: float = Field(0.8, ge=0, le=1, description="Prediction confidence")
    forecast_date: datetime = Field(default_factory=datetime.utcnow)


class CropRecommendation(BaseModel):
    """Single crop recommendation with minimal data."""
    crop_id: str
    crop_name: str
    viability_score: float = Field(..., ge=0, le=1)
    water_requirement_mm: float


class UserWaterDocument(BaseModel):
    """
    Complete user document for Firestore.
    
    Target size: <5KB per document.
    
    What we store:
    - Final prediction values (single numbers)
    - Top 3 crop recommendations
    - Aggregated statistics (mean, min, max)
    - User preferences
    
    What we DO NOT store:
    - Raw NetCDF data
    - Complete time series
    - Full training data
    - Large numpy arrays
    """
    user_id: str
    location: LocationData
    water_status: WaterStatusSummary
    recommendations: List[str] = Field(
        default_factory=list, 
        max_length=5,  # Limit to top 5 crops
        description="Top crop IDs"
    )
    recommendation_details: Optional[List[CropRecommendation]] = Field(
        None,
        max_length=3,  # Only top 3 with full details
    )
    forecast_summary: Optional[ForecastSummary] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Reference to cloud storage for heavy data (if needed)
    raw_data_url: Optional[str] = Field(
        None, 
        description="GCS URL for full forecast data (gs://bucket/path)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "abc123",
                "location": {"lat": 19.2183, "lon": 72.9781, "city": "Thane", "state": "Maharashtra"},
                "water_status": {
                    "percentage": 6.0,
                    "mm": 30.0,
                    "status": "CRITICAL",
                    "last_updated": "2026-02-06T18:00:00Z"
                },
                "recommendations": ["wheat", "pulses", "cotton"],
                "forecast_summary": {
                    "next_week_avg_mm": 45.0,
                    "confidence": 0.87
                }
            }
        }


def estimate_document_size(doc: UserWaterDocument) -> int:
    """Estimate Firestore document size in bytes."""
    import json
    json_str = doc.model_dump_json()
    return len(json_str.encode('utf-8'))


# Size validation
def validate_document_size(doc: UserWaterDocument, max_kb: int = 10) -> bool:
    """Ensure document is under the size limit."""
    size_bytes = estimate_document_size(doc)
    return size_bytes < (max_kb * 1024)
