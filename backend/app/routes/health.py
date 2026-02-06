from fastapi import APIRouter
from schemas.response import HealthResponse
from datetime import datetime

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return HealthResponse(
        status="healthy",
        message="API is running smoothly",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
