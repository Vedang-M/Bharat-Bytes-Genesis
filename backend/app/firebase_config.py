"""
Firebase Configuration
Initializes Firebase Admin SDK for authentication and Firestore access.

Credentials loading priority:
1. FIREBASE_CREDENTIALS env variable (JSON string - for production)
2. FIREBASE_SERVICE_ACCOUNT_PATH env variable (file path)
3. Default file locations (firebase-service-account.json)

SECURITY: Never commit service account JSON to git!
"""

import os
import json
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Any

# Try to import firebase_admin, gracefully handle if not installed
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    credentials = None
    firestore = None
    auth = None

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_firebase_credentials():
    """
    Get Firebase credentials from environment or file.
    
    Priority:
    1. FIREBASE_CREDENTIALS env var (JSON string)
    2. FIREBASE_SERVICE_ACCOUNT_PATH env var (file path)
    3. Default file locations
    
    Returns:
        credentials.Certificate or None
    """
    if not FIREBASE_AVAILABLE:
        return None
    
    # Option 1: JSON string in environment variable (recommended for production)
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if cred_json:
        try:
            cred_dict = json.loads(cred_json)
            return credentials.Certificate(cred_dict)
        except json.JSONDecodeError as e:
            print(f"Error parsing FIREBASE_CREDENTIALS: {e}")
            return None
    
    # Option 2: File path from environment variable
    env_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if env_path:
        path = Path(env_path) if Path(env_path).is_absolute() else PROJECT_ROOT / env_path
        if path.exists():
            return credentials.Certificate(str(path))
    
    # Option 3: Default file locations
    default_paths = [
        PROJECT_ROOT / "firebase-service-account.json",
        PROJECT_ROOT / "serviceAccountKey.json",
        PROJECT_ROOT / "backend" / "firebase-service-account.json",
    ]
    
    for path in default_paths:
        if path.exists():
            return credentials.Certificate(str(path))
    
    return None


def initialize_firebase() -> bool:
    """
    Initialize Firebase Admin SDK.
    Returns True if successful, False otherwise.
    """
    if not FIREBASE_AVAILABLE:
        print("Warning: firebase-admin package not installed. Run: pip install firebase-admin")
        return False
    
    # Check if already initialized
    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        pass  # Not initialized yet
    
    cred = get_firebase_credentials()
    
    if not cred:
        print("Warning: Firebase credentials not found.")
        print("Firebase features will be disabled. To enable, set one of:")
        print("1. FIREBASE_CREDENTIALS env var (JSON string)")
        print("2. FIREBASE_SERVICE_ACCOUNT_PATH env var (file path)")
        print("3. Place firebase-service-account.json in project root")
        return False
    
    try:
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False


@lru_cache(maxsize=1)
def get_firestore_client():
    """
    Get Firestore database client.
    Returns None if Firebase is not initialized.
    """
    if not FIREBASE_AVAILABLE:
        return None
    
    try:
        firebase_admin.get_app()
        return firestore.client()
    except ValueError:
        if initialize_firebase():
            return firestore.client()
        return None


def get_auth():
    """
    Get Firebase Auth instance.
    Returns None if Firebase is not initialized.
    """
    if not FIREBASE_AVAILABLE:
        return None
    
    try:
        firebase_admin.get_app()
        return auth
    except ValueError:
        if initialize_firebase():
            return auth
        return None


def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a Firebase ID token and return the decoded claims.
    
    Args:
        id_token: The Firebase ID token from the client
        
    Returns:
        dict with user info (uid, email, etc.) or None if invalid
    """
    auth_module = get_auth()
    if not auth_module:
        return None
    
    try:
        decoded_token = auth_module.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None


# ==================== AUTHENTICATED FIRESTORE OPERATIONS ====================

async def save_user_data(user_token: str, data: Dict[str, Any]) -> bool:
    """
    Save user data to Firestore with JWT verification.
    
    Args:
        user_token: Firebase ID token from client
        data: Data to save (must conform to UserWaterDocument schema)
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If token is invalid or user is unauthorized
    """
    # Verify the token first
    decoded = verify_firebase_token(user_token)
    if not decoded:
        raise ValueError("Invalid or expired authentication token")
    
    uid = decoded.get("uid")
    if not uid:
        raise ValueError("Token does not contain user ID")
    
    db = get_firestore_client()
    if not db:
        raise RuntimeError("Firestore not available")
    
    # Add uid to data for reference
    data["user_id"] = uid
    
    # Save to Firestore
    try:
        db.collection("users").document(uid).set(data, merge=True)
        return True
    except Exception as e:
        print(f"Firestore write error: {e}")
        return False


async def get_user_data(user_token: str) -> Optional[Dict[str, Any]]:
    """
    Get user data from Firestore with JWT verification.
    
    Args:
        user_token: Firebase ID token from client
    
    Returns:
        User data dict or None if not found
    
    Raises:
        ValueError: If token is invalid
    """
    decoded = verify_firebase_token(user_token)
    if not decoded:
        raise ValueError("Invalid or expired authentication token")
    
    uid = decoded.get("uid")
    if not uid:
        raise ValueError("Token does not contain user ID")
    
    db = get_firestore_client()
    if not db:
        return None
    
    try:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Firestore read error: {e}")
        return None


async def update_user_water_status(
    user_token: str,
    water_percentage: float,
    water_mm: float,
    status: str,
    recommendations: list = None
) -> bool:
    """
    Update user's water status document with JWT verification.
    
    This is a specialized function for the main use case.
    """
    from datetime import datetime, timezone
    
    data = {
        "water_status": {
            "percentage": water_percentage,
            "mm": water_mm,
            "status": status,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    }
    
    if recommendations:
        data["recommendations"] = recommendations[:5]  # Limit to top 5
    
    return await save_user_data(user_token, data)


# Firestore collection names
COLLECTIONS = {
    "users": "users",
    "farms": "farms",
    "predictions": "predictions",
    "notifications": "notifications",
}
