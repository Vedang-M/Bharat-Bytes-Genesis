"""
Health Check Routes
"""

import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter

# Check ML availability
ml_path = Path(__file__).parent.parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path.parent))

try:
    from ml import CROP_DATABASE, get_model
    ML_AVAILABLE = True
    MODELS_READY = False
    try:
        model = get_model()
        MODELS_READY = model.models_ready()
    except Exception:
        pass
except ImportError:
    ML_AVAILABLE = False
    MODELS_READY = False
    CROP_DATABASE = {}

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Water Wallet API",
        "ml_available": ML_AVAILABLE,
        "ml_models_ready": MODELS_READY,
        "crops_available": len(CROP_DATABASE) if CROP_DATABASE else 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Water Wallet API",
        "description": "AI-Based Solvency System for Small & Marginal Farmers",
        "version": "1.0.0",
        "docs": "/docs",
        "ml_available": ML_AVAILABLE,
        "endpoints": {
            "simplified": {
                "GET /api/water-status": "Get water status (lat, lon query params)",
                "GET /api/crop-check/{crop_id}": "Check crop viability (lat, lon query params)",
                "GET /api/smart-swap/{rejected_crop_id}": "Get alternative crops (water_mm query param)",
                "GET /api/crops": "List all supported crops",
            },
            "full": {
                "POST /api/water-status": "Get water status with full location details",
                "POST /api/crop-viability": "Check crop viability with location",
                "POST /api/crop-alternatives": "Get alternative crops",
                "POST /api/best-sowing-date": "Get best sowing date",
                "GET /api/profit-ranking": "Get crops ranked by profit-per-drop",
            },
        },
    }
