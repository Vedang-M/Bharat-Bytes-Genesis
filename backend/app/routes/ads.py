"""
Fertilizer Ads Routes
API endpoints for government-approved fertilizer advertisements.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from ..schemas.ads import FertilizerAdResponse, AdsListResponse
from ..services.ads_service import get_ads, get_ad_by_id, seed_sample_ads

router = APIRouter(
    prefix="/api",
    tags=["Fertilizer Ads"],
)


@router.get(
    "/ads",
    response_model=AdsListResponse,
    summary="Get Fertilizer Ads",
    description="""
    Fetch government-approved fertilizer advertisements filtered by crop, region, and season.
    
    Returns maximum 2 ads per request to avoid overwhelming the UI.
    Only returns active, government-approved ads.
    
    **Filters:**
    - `crop`: Filter by target crop (e.g., "wheat", "rice", "cotton")
    - `region`: Filter by target region/state (e.g., "Maharashtra", "Punjab")
    - `season`: Filter by target season ("kharif", "rabi", "zaid")
    """
)
async def get_fertilizer_ads(
    crop: Optional[str] = Query(
        None,
        description="Target crop to filter by",
        example="wheat"
    ),
    region: Optional[str] = Query(
        None,
        description="Target region/state to filter by",
        example="Maharashtra"
    ),
    season: Optional[str] = Query(
        "kharif",
        description="Target season (kharif/rabi/zaid)",
        example="kharif"
    )
) -> AdsListResponse:
    """
    Get filtered fertilizer ads.
    
    - Only returns government-approved, active ads
    - Maximum 2 ads returned per request
    - Filters can be combined
    """
    ads = await get_ads(
        crop=crop,
        region=region,
        season=season,
        limit=2
    )
    
    # Convert to response format
    ad_responses = [
        FertilizerAdResponse(
            id=ad.get('id', ''),
            brand_name=ad.get('brand_name', ''),
            product_name=ad.get('product_name', ''),
            image_url=ad.get('image_url', ''),
            approval_number=ad.get('approval_number', ''),
            target_crops=ad.get('target_crops', []),
            target_season=ad.get('target_season', ''),
            price_per_unit=ad.get('price_per_unit', 0.0),
            unit=ad.get('unit', ''),
            retailer_links=ad.get('retailer_links', [])
        )
        for ad in ads
    ]
    
    return AdsListResponse(
        ads=ad_responses,
        count=len(ad_responses),
        filters_applied={
            "crop": crop,
            "region": region,
            "season": season
        }
    )


@router.get(
    "/ads/{ad_id}",
    response_model=FertilizerAdResponse,
    summary="Get Single Ad",
    description="Fetch a single fertilizer ad by its ID."
)
async def get_single_ad(ad_id: str) -> FertilizerAdResponse:
    """Get a specific ad by ID."""
    ad = await get_ad_by_id(ad_id)
    
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return FertilizerAdResponse(
        id=ad.get('id', ''),
        brand_name=ad.get('brand_name', ''),
        product_name=ad.get('product_name', ''),
        image_url=ad.get('image_url', ''),
        approval_number=ad.get('approval_number', ''),
        target_crops=ad.get('target_crops', []),
        target_season=ad.get('target_season', ''),
        price_per_unit=ad.get('price_per_unit', 0.0),
        unit=ad.get('unit', ''),
        retailer_links=ad.get('retailer_links', [])
    )


@router.post(
    "/ads/seed",
    summary="Seed Sample Ads",
    description="Populate database with sample government-approved fertilizer ads. For development use."
)
async def seed_ads():
    """
    Seed the database with sample ads.
    This is for development/testing purposes.
    """
    count = await seed_sample_ads()
    return {
        "message": f"Successfully seeded {count} sample ads",
        "count": count
    }
