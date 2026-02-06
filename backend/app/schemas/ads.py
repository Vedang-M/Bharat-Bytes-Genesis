"""
Fertilizer Ads Schemas
Pydantic models for government-approved fertilizer advertisements.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FertilizerAd(BaseModel):
    """Fertilizer advertisement document schema."""
    id: str = Field(..., description="Unique ad identifier")
    brand_name: str = Field(..., description="Brand/manufacturer name")
    product_name: str = Field(..., description="Product name")
    image_url: str = Field(..., description="Product image URL")
    government_approved: bool = Field(default=True, description="Government approval status")
    approval_number: str = Field(..., description="FCO approval number")
    target_crops: List[str] = Field(default=[], description="Target crop IDs")
    target_regions: List[str] = Field(default=[], description="Target states/regions")
    target_season: str = Field(..., description="Target season (kharif/rabi/zaid)")
    price_per_unit: float = Field(..., description="Price per unit in INR")
    unit: str = Field(..., description="Unit description (e.g., '500ml bottle')")
    retailer_links: List[str] = Field(default=[], description="Purchase links")
    active: bool = Field(default=True, description="Ad active status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ad_001",
                "brand_name": "IFFCO",
                "product_name": "Nano Urea",
                "image_url": "https://storage.googleapis.com/fertilizer-ads/iffco_urea.jpg",
                "government_approved": True,
                "approval_number": "FCO/2023/1234",
                "target_crops": ["wheat", "rice", "cotton"],
                "target_regions": ["Maharashtra", "Punjab"],
                "target_season": "kharif",
                "price_per_unit": 266.50,
                "unit": "500ml bottle",
                "retailer_links": ["https://retailer1.com", "https://retailer2.com"],
                "active": True,
                "created_at": "2026-01-15T10:00:00Z"
            }
        }


class FertilizerAdResponse(BaseModel):
    """Response model for a single fertilizer ad."""
    id: str
    brand_name: str
    product_name: str
    image_url: str
    approval_number: str
    target_crops: List[str]
    target_season: str
    price_per_unit: float
    unit: str
    retailer_links: List[str]


class AdsListResponse(BaseModel):
    """Response model for ads list endpoint."""
    ads: List[FertilizerAdResponse]
    count: int = Field(..., description="Number of ads returned")
    filters_applied: dict = Field(default={}, description="Applied filters")
