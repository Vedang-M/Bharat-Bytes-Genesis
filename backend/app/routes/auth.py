"""
Authentication Routes
User registration, login, and profile management.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field

from ..firebase_config import get_auth, verify_firebase_token, get_firestore_client, COLLECTIONS
from ..middleware.auth_middleware import get_current_user, get_current_user_optional, AuthenticatedUser
from ..services.db_service import get_db_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ==================== REQUEST/RESPONSE SCHEMAS ====================

class RegisterRequest(BaseModel):
    """User registration request."""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r"^\d{10}$")
    email: Optional[EmailStr] = None
    role: str = Field(default="farmer", pattern="^(farmer|sarpanch|admin)$")
    location: Optional[dict] = Field(default=None, description="User location {lat, lon, state, district, block}")
    firebase_uid: str = Field(..., description="Firebase Auth UID from client")


class LoginRequest(BaseModel):
    """Login request with Firebase ID token."""
    id_token: str = Field(..., description="Firebase ID token from client")


class ProfileUpdateRequest(BaseModel):
    """Profile update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\d{10}$")
    location: Optional[dict] = None


class UserResponse(BaseModel):
    """User profile response."""
    uid: str
    name: str
    phone: str
    email: Optional[str] = None
    role: str
    location: Optional[dict] = None
    createdAt: Optional[str] = None


# ==================== ENDPOINTS ====================

@router.post("/register", response_model=UserResponse)
async def register_user(request: RegisterRequest):
    """
    Register a new user in Firestore.
    
    This should be called after Firebase Auth signup on the client.
    The client provides the Firebase UID after successful signup.
    """
    db_service = get_db_service()
    
    if not db_service.is_available():
        # If Firebase isn't configured, return a mock response for development
        return UserResponse(
            uid=request.firebase_uid,
            name=request.name,
            phone=request.phone,
            email=request.email,
            role=request.role,
            location=request.location,
            createdAt=datetime.utcnow().isoformat(),
        )
    
    # Check if user already exists
    existing = await db_service.get_user(request.firebase_uid)
    if existing:
        raise HTTPException(status_code=400, detail="User already registered")
    
    # Create user document
    user_data = await db_service.create_user(
        uid=request.firebase_uid,
        data={
            "name": request.name,
            "phone": request.phone,
            "email": request.email,
            "role": request.role,
            "location": request.location or {},
        }
    )
    
    return UserResponse(
        uid=user_data["uid"],
        name=user_data["name"],
        phone=user_data["phone"],
        email=user_data.get("email"),
        role=user_data["role"],
        location=user_data.get("location"),
        createdAt=user_data["createdAt"].isoformat() if user_data.get("createdAt") else None,
    )


@router.post("/login", response_model=UserResponse)
async def login_user(request: LoginRequest):
    """
    Login with Firebase ID token.
    
    Verifies the token, fetches user profile, and updates last login.
    """
    # Verify token
    decoded = verify_firebase_token(request.id_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    uid = decoded["uid"]
    db_service = get_db_service()
    
    if not db_service.is_available():
        # Development mode response
        return UserResponse(
            uid=uid,
            name="Dev User",
            phone="0000000000",
            email=decoded.get("email"),
            role="farmer",
            location=None,
            createdAt=datetime.utcnow().isoformat(),
        )
    
    # Get user from Firestore
    user = await db_service.get_user(uid)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not registered. Please sign up first.")
    
    # Update last login
    await db_service.update_last_login(uid)
    
    return UserResponse(
        uid=user["uid"],
        name=user["name"],
        phone=user["phone"],
        email=user.get("email"),
        role=user["role"],
        location=user.get("location"),
        createdAt=user["createdAt"].isoformat() if user.get("createdAt") else None,
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(user: AuthenticatedUser = Depends(get_current_user)):
    """Get authenticated user's profile."""
    db_service = get_db_service()
    
    if not db_service.is_available():
        return UserResponse(
            uid=user.uid,
            name=user.name or "Dev User",
            phone=user.phone or "0000000000",
            email=user.email,
            role=user.role,
            location=user.location,
        )
    
    user_data = await db_service.get_user(user.uid)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        uid=user_data["uid"],
        name=user_data["name"],
        phone=user_data["phone"],
        email=user_data.get("email"),
        role=user_data["role"],
        location=user_data.get("location"),
        createdAt=user_data["createdAt"].isoformat() if user_data.get("createdAt") else None,
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Update authenticated user's profile."""
    db_service = get_db_service()
    
    if not db_service.is_available():
        return UserResponse(
            uid=user.uid,
            name=request.name or user.name or "Dev User",
            phone=request.phone or user.phone or "0000000000",
            email=user.email,
            role=user.role,
            location=request.location or user.location,
        )
    
    update_data = {}
    if request.name:
        update_data["name"] = request.name
    if request.phone:
        update_data["phone"] = request.phone
    if request.location:
        update_data["location"] = request.location
    
    user_data = await db_service.update_user(user.uid, update_data)
    
    return UserResponse(
        uid=user_data["uid"],
        name=user_data["name"],
        phone=user_data["phone"],
        email=user_data.get("email"),
        role=user_data["role"],
        location=user_data.get("location"),
        createdAt=user_data["createdAt"].isoformat() if user_data.get("createdAt") else None,
    )


@router.get("/check")
async def check_auth(user: AuthenticatedUser = Depends(get_current_user_optional)):
    """
    Check if user is authenticated.
    Returns user info if authenticated, null otherwise.
    """
    if user:
        return {
            "authenticated": True,
            "user": {
                "uid": user.uid,
                "email": user.email,
                "role": user.role,
                "name": user.name,
            }
        }
    return {"authenticated": False, "user": None}
