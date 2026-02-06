from fastapi import APIRouter, Query
from typing import Optional
from ..services.water_balance import get_water_availability

router = APIRouter(prefix="/api", tags=["water"])


@router.get("/water-status")
def water_status(
    district: Optional[str] = Query(None, description="District name"),
    state: Optional[str] = Query(None, description="State name"),
):
    """
    Returns water availability for a given district/state.
    Used by the WaterStatusScreen on the frontend.
    """
    return get_water_availability(district, state)
