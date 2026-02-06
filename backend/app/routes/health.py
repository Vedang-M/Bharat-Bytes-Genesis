"""
Health Check Routes
"""

from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Water Wallet API",
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
        "endpoints": [
            "/api/water-status",
            "/api/crop-viability",
            "/api/crop-alternatives",
            "/api/best-sowing-date",
            "/api/crops",
            "/api/profit-ranking",
            "/health",
        ],
    }
