import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from firebase_admin import auth

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

class AssignRoleRequest(BaseModel):
    """Request to manually assign a role."""
    uid: str
    role: str = Field(..., pattern="^(farmer|sarpanch|admin)$")


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

    # Secure Role Validation
    final_role = "farmer" # Default safest role
    
    # Parse authorized emails
    admin_emails = [e.strip() for e in os.getenv("AUTHORIZED_ADMIN_EMAILS", "").split(",") if e.strip()]
    sarpanch_emails = [e.strip() for e in os.getenv("AUTHORIZED_SARPANCH_EMAILS", "").split(",") if e.strip()]
    
    if request.role == "admin":
        if request.email and request.email in admin_emails:
            final_role = "admin"
        else:
            final_role = "farmer" # Fallback if unauthorized
        
    elif request.role == "sarpanch":
        if request.email and request.email in sarpanch_emails:
            final_role = "sarpanch"
        else:
            final_role = "farmer" # Fallback if unauthorized
            
    else:
        final_role = "farmer"

    # Set Firebase Custom Claims for Role (if not farmer)
    if final_role != "farmer":
        try:
            auth.set_custom_user_claims(request.firebase_uid, {'role': final_role})
            print(f"Set custom claim role='{final_role}' for user {request.email}")
        except Exception as e:
            print(f"Error setting custom claims: {e}")
            # Continue anyway, we still store role in Firestore
    
    # Create user document
    user_data = await db_service.create_user(
        uid=request.firebase_uid,
        data={
            "name": request.name,
            "phone": request.phone,
            "email": request.email,
            "role": final_role,
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


@router.post("/assign-role")
async def assign_role(
    request: AssignRoleRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Admin-only endpoint to manually assign roles.
    Updates both Firestore and Firebase Auth Custom Claims.
    """
    # 1. Verify caller is Admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Admin access required.")

    db_service = get_db_service()
    
    # 2. Update Firestore
    try:
        updated_user = await db_service.update_user(request.uid, {"role": request.role})
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firestore update failed: {str(e)}")

    # 3. Update Firebase Custom Claims
    try:
        # If role is 'farmer', we can remove the claim or set it to farmer.
        # Setting explicitly is safer.
        auth.set_custom_user_claims(request.uid, {'role': request.role})
    except Exception as e:
        print(f"Error setting custom claims: {e}")
        # We don't fail the request here, but we should log it
        
    return {
        "success": True, 
        "message": f"Role '{request.role}' assigned to user {request.uid}",
        "user": updated_user
    }
