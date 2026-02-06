"""
Authentication Middleware
JWT token verification and role-based access control.
"""

from functools import wraps
from typing import Optional, List, Callable
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..firebase_config import verify_firebase_token, get_firestore_client, COLLECTIONS

# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    """Represents an authenticated user from Firebase."""
    
    def __init__(self, uid: str, email: str = None, role: str = "farmer", 
                 name: str = None, phone: str = None, location: dict = None):
        self.uid = uid
        self.email = email
        self.role = role
        self.name = name
        self.phone = phone
        self.location = location or {}
    
    def has_role(self, required_role: str) -> bool:
        """Check if user has required role or higher."""
        role_hierarchy = {"farmer": 0, "sarpanch": 1, "admin": 2}
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level
    
    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "email": self.email,
            "role": self.role,
            "name": self.name,
            "phone": self.phone,
            "location": self.location,
        }


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[AuthenticatedUser]:
    """
    Get current user if authenticated, None otherwise.
    Use this for endpoints that work with or without auth.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    decoded = verify_firebase_token(token)
    
    if not decoded:
        return None
    
    # Get user data from Firestore
    db = get_firestore_client()
    if db:
        try:
            user_doc = db.collection(COLLECTIONS["users"]).document(decoded["uid"]).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return AuthenticatedUser(
                    uid=decoded["uid"],
                    email=decoded.get("email"),
                    role=user_data.get("role", "farmer"),
                    name=user_data.get("name"),
                    phone=user_data.get("phone"),
                    location=user_data.get("location"),
                )
        except Exception as e:
            print(f"Error fetching user data: {e}")
    
    # Return basic user from token if Firestore unavailable
    return AuthenticatedUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        role="farmer",
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """
    Get current authenticated user.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = credentials.credentials
    decoded = verify_firebase_token(token)
    
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user data from Firestore
    db = get_firestore_client()
    if db:
        try:
            user_doc = db.collection(COLLECTIONS["users"]).document(decoded["uid"]).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return AuthenticatedUser(
                    uid=decoded["uid"],
                    email=decoded.get("email"),
                    role=user_data.get("role", "farmer"),
                    name=user_data.get("name"),
                    phone=user_data.get("phone"),
                    location=user_data.get("location"),
                )
        except Exception as e:
            print(f"Error fetching user data: {e}")
    
    return AuthenticatedUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        role="farmer",
    )


def require_role(required_role: str):
    """
    Dependency that requires a specific role level.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: AuthenticatedUser = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> AuthenticatedUser:
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = credentials.credentials
        decoded = verify_firebase_token(token)
        
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Get user role from Firestore
        db = get_firestore_client()
        user_role = "farmer"
        user_data = {}
        
        if db:
            try:
                user_doc = db.collection(COLLECTIONS["users"]).document(decoded["uid"]).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    user_role = user_data.get("role", "farmer")
            except Exception as e:
                print(f"Error fetching user role: {e}")
        
        user = AuthenticatedUser(
            uid=decoded["uid"],
            email=decoded.get("email"),
            role=user_role,
            name=user_data.get("name"),
            phone=user_data.get("phone"),
            location=user_data.get("location"),
        )
        
        if not user.has_role(required_role):
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role: {required_role}"
            )
        
        return user
    
    return role_checker
