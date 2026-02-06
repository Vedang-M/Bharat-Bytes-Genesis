from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes.water_status import router as water_router
from routes.health import router as health_router

# Initialize FastAPI app
app = FastAPI(
    title="Bharat Bytes Genesis API",
    description="API for water availability and crop recommendation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API key from environment variable
EXPECTED_API_KEY = os.getenv("API_KEY", "bharat-bytes-genesis-2026-api-key-v1")


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key from request header.
    Public endpoints don't require API key verification.
    """
    if api_key == EXPECTED_API_KEY:
        return api_key
    # For public endpoints, we'll make API key optional
    return None


# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(water_router, prefix="/api", tags=["Water & Crops"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bharat Bytes Genesis API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status": "error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "status": "error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
