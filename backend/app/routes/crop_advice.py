from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.crop_advisor import get_crop_advice


class CropAdviceRequest(BaseModel):
    crop_id: str
    water_availability: int
    district: Optional[str] = None
    state: Optional[str] = None
    language: str = "hi"


router = APIRouter(prefix="/api", tags=["crops"])


@router.post("/crop-advice")
def crop_advice(req: CropAdviceRequest):
    """
    Returns crop recommendation based on selected crop and water availability.
    Used by the CropResult screen on the frontend.
    """
    return get_crop_advice(req.crop_id, req.water_availability, req.language)
