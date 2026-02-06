"""
Water Wallet Backend API
FastAPI application for the Village-Level Water Accountant system.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add ml module to path for imports
ml_path = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ml_path.parent))

from .routes import water_status, health, ml, auth, admin
from .firebase_config import initialize_firebase

# ... (lines 20-84 omitted) ...

# Include routers
app.include_router(health.router)
app.include_router(water_status.router)
app.include_router(ml.router)
app.include_router(auth.router)
app.include_router(admin.router)




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Pre-loads ML models and initializes Firebase on startup.
    """
    # Startup: Initialize Firebase
    print("Initializing Firebase...")
    firebase_ok = initialize_firebase()
    if firebase_ok:
        print("Firebase initialized successfully!")
    else:
        print("Firebase not configured - running in development mode")
    
    # Startup: Load ML models
    print("Loading ML models...")
    try:
        from ml import get_model
        model = get_model()
        print("ML models loaded successfully!")
    except Exception as e:
        print(f"Warning: Could not pre-load ML models: {e}")
    
    yield
    
    # Shutdown: Cleanup if needed
    print("Shutting down Water Wallet API...")


# Create FastAPI app
app = FastAPI(
    title="Water Wallet API",
    description="""
    ## AI-Based Solvency System for Small & Marginal Farmers
    
    This API provides:
    - **Water Balance Prediction**: Calculate available water for a location
    - **Crop Viability Analysis**: Check if a crop can be sustained
    - **Smart-Swap Recommendations**: Get alternative crops with better water efficiency
    - **Profit-Per-Drop Calculator**: Rank crops by financial return per liter of water
    - **Best Sowing Date**: Optimal planting date based on weather forecast
    - **User Authentication**: Firebase-based auth with role support (farmer/sarpanch/admin)
    
    ### Data Sources
    - Weather: Visual Crossing API (15-day forecast)
    - Groundwater: CGWB 2024 Assessment data
    - Soil: ISRIC SoilGrids 2.0
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(water_status.router)
app.include_router(ml.router)
app.include_router(auth.router)

