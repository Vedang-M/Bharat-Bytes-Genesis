"""
Firebase Configuration
Initializes Firebase Admin SDK for authentication and Firestore access.
"""

import os
from pathlib import Path
from functools import lru_cache

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


def get_firebase_credentials_path() -> Path:
    """Get path to Firebase service account JSON file."""
    # Check environment variable first
    env_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if env_path:
        path = Path(env_path)
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path
    
    # Default locations to check
    default_paths = [
        PROJECT_ROOT / "firebase-service-account.json",
        PROJECT_ROOT / "serviceAccountKey.json",
        PROJECT_ROOT / "backend" / "firebase-service-account.json",
    ]
    
    for path in default_paths:
        if path.exists():
            return path
    
    return default_paths[0]  # Return default path even if doesn't exist


def initialize_firebase():
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
    
    cred_path = get_firebase_credentials_path()
    
    if not cred_path.exists():
        print(f"Warning: Firebase credentials not found at {cred_path}")
        print("Firebase features will be disabled. To enable:")
        print("1. Go to Firebase Console > Project Settings > Service Accounts")
        print("2. Click 'Generate new private key'")
        print("3. Save as 'firebase-service-account.json' in project root")
        return False
    
    try:
        cred = credentials.Certificate(str(cred_path))
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


def verify_firebase_token(id_token: str) -> dict | None:
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


# Firestore collection names
COLLECTIONS = {
    "users": "users",
    "farms": "farms",
    "predictions": "predictions",
    "notifications": "notifications",
}
