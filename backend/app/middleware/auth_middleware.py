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


def require_role(*allowed_roles: str):
    """
    Dependency that requires one of the allowed roles.
    Checks Firebase Custom Claims in the JWT token.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user_role: str = Depends(require_role("admin"))):
            ...
            
        @router.get("/sarpanch-or-admin")
        async def restricted_endpoint(user_role: str = Depends(require_role("sarpanch", "admin"))):
            ...
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> str:
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = credentials.credentials
        decoded = verify_firebase_token(token)
        
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Get role from Custom Claims (fallback to 'farmer' if not set)
        user_role = decoded.get("role", "farmer")
        
        # Determine if user has access based on role hierarchy
        # Access Check:
        # 1. Exact match in allowed_roles?
        # 2. Or is user_role higher level than required?
        
        # To simplify, we can check if user_role is in allowed_roles
        # OR we can implement hierarchy check if a single minimum role is passed.
        # The prompt asked for: require_role("farmer"|"sarpanch"|"admin")
        
        # Let's support both explicit list AND hierarchy if single arg is passed
        hierarchy = {"farmer": 0, "sarpanch": 1, "admin": 2}
        user_level = hierarchy.get(user_role, 0)
        
        has_access = False
        
        if user_role in allowed_roles:
            has_access = True
            
        # Hierarchy check if user has higher role than requested
        # e.g. require_role("sarpanch") -> admin should also be allowed?
        # Usually yes.
        for required in allowed_roles:
            req_level = hierarchy.get(required, 100)
            if user_level >= req_level:
                has_access = True
                break
                
        if not has_access:
             raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role: {allowed_roles}. Your role: {user_role}"
            )
        
        return user_role
    
    return role_checker
