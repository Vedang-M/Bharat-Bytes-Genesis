"""
Database Service
Firestore CRUD operations for users, farms, predictions, and notifications.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from ..firebase_config import get_firestore_client, COLLECTIONS


class DatabaseService:
    """Service class for Firestore database operations."""
    
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db
    
    def is_available(self) -> bool:
        """Check if database is available."""
        return self.db is not None
    
    # ==================== USER OPERATIONS ====================
    
    async def create_user(self, uid: str, data: dict) -> dict:
        """
        Create a new user document in Firestore.
        
        Args:
            uid: Firebase Auth user ID
            data: User data (name, phone, email, role, location)
        
        Returns:
            Created user data with timestamps
        """
        if not self.db:
            raise RuntimeError("Database not available")
        
        user_data = {
            "name": data.get("name", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "role": data.get("role", "farmer"),
            "location": data.get("location", {}),
            "farmIds": [],
            "createdAt": datetime.utcnow(),
            "lastLogin": datetime.utcnow(),
        }
        
        self.db.collection(COLLECTIONS["users"]).document(uid).set(user_data)
        return {"uid": uid, **user_data}
    
    async def get_user(self, uid: str) -> Optional[dict]:
        """Get user by Firebase UID."""
        if not self.db:
            return None
        
        doc = self.db.collection(COLLECTIONS["users"]).document(uid).get()
        if doc.exists:
            return {"uid": uid, **doc.to_dict()}
        return None
    
    async def update_user(self, uid: str, data: dict) -> dict:
        """Update user document."""
        if not self.db:
            raise RuntimeError("Database not available")
        
        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updatedAt"] = datetime.utcnow()
        
        self.db.collection(COLLECTIONS["users"]).document(uid).update(update_data)
        return await self.get_user(uid)
    
    async def update_last_login(self, uid: str):
        """Update user's last login timestamp."""
        if self.db:
            self.db.collection(COLLECTIONS["users"]).document(uid).update({
                "lastLogin": datetime.utcnow()
            })
    
    async def get_users_by_role(self, role: str) -> List[dict]:
        """Get all users with a specific role."""
        if not self.db:
            return []
        
        docs = self.db.collection(COLLECTIONS["users"]).where("role", "==", role).stream()
        return [{"uid": doc.id, **doc.to_dict()} for doc in docs]
    
    async def get_users_by_location(self, state: str = None, district: str = None) -> List[dict]:
        """Get users filtered by location."""
        if not self.db:
            return []
        
        query = self.db.collection(COLLECTIONS["users"])
        
        if state:
            query = query.where("location.state", "==", state)
        if district:
            query = query.where("location.district", "==", district)
        
        docs = query.stream()
        return [{"uid": doc.id, **doc.to_dict()} for doc in docs]

    async def get_all_users(self, limit: int = 50) -> List[dict]:
        """
        Get all users with pagination limit.
        Used for Admin Dashboard.
        """
        if not self.db:
            return []
        
        # Order by creation time if available, otherwise just limit
        try:
            query = self.db.collection(COLLECTIONS["users"]).order_by(
                "createdAt", direction="DESCENDING"
            ).limit(limit)
        except Exception:
            # Fallback if index missing or createdAt missing
            query = self.db.collection(COLLECTIONS["users"]).limit(limit)
            
        docs = query.stream()
        return [{"uid": doc.id, **doc.to_dict()} for doc in docs]
    
    # ==================== FARM OPERATIONS ====================
    
    async def create_farm(self, user_id: str, data: dict) -> dict:
        """Create a new farm for a user."""
        if not self.db:
            raise RuntimeError("Database not available")
        
        farm_data = {
            "userId": user_id,
            "name": data.get("name", "My Farm"),
            "area_hectares": data.get("area_hectares", 0),
            "location": data.get("location", {}),
            "currentCrop": data.get("currentCrop"),
            "createdAt": datetime.utcnow(),
        }
        
        doc_ref = self.db.collection(COLLECTIONS["farms"]).add(farm_data)
        farm_id = doc_ref[1].id
        
        # Add farm ID to user's farmIds array
        self.db.collection(COLLECTIONS["users"]).document(user_id).update({
            "farmIds": firestore.ArrayUnion([farm_id])
        })
        
        return {"id": farm_id, **farm_data}
    
    async def get_farms_for_user(self, user_id: str) -> List[dict]:
        """Get all farms for a user."""
        if not self.db:
            return []
        
        docs = self.db.collection(COLLECTIONS["farms"]).where("userId", "==", user_id).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    
    # ==================== PREDICTION LOGGING ====================
    
    async def log_prediction(
        self, 
        user_id: str, 
        prediction_type: str, 
        input_data: dict, 
        result: dict,
        model: str = "unknown",
        farm_id: str = None
    ) -> str:
        """
        Log a prediction for analytics and history.
        
        Args:
            user_id: User who made the request
            prediction_type: "water_status", "crop_viability", "groundwater", etc.
            input_data: Request parameters
            result: Prediction result
            model: ML model used
            farm_id: Optional associated farm
        
        Returns:
            Prediction document ID
        """
        if not self.db:
            return None
        
        prediction_data = {
            "userId": user_id,
            "farmId": farm_id,
            "type": prediction_type,
            "input": input_data,
            "result": result,
            "model": model,
            "timestamp": datetime.utcnow(),
        }
        
        doc_ref = self.db.collection(COLLECTIONS["predictions"]).add(prediction_data)
        return doc_ref[1].id
    
    async def get_predictions_for_user(
        self, 
        user_id: str, 
        prediction_type: str = None,
        limit: int = 20
    ) -> List[dict]:
        """Get prediction history for a user."""
        if not self.db:
            return []
        
        query = self.db.collection(COLLECTIONS["predictions"]).where("userId", "==", user_id)
        
        if prediction_type:
            query = query.where("type", "==", prediction_type)
        
        query = query.order_by("timestamp", direction="DESCENDING").limit(limit)
        
        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    
    # ==================== NOTIFICATIONS ====================
    
    async def create_notification(
        self, 
        from_user_id: str, 
        message: str,
        notification_type: str = "info",
        village: str = None,
        state: str = None,
        district: str = None
    ) -> str:
        """Create a notification (typically from Sarpanch)."""
        if not self.db:
            return None
        
        notification_data = {
            "fromUserId": from_user_id,
            "message": message,
            "type": notification_type,  # info, warning, critical
            "village": village,
            "state": state,
            "district": district,
            "createdAt": datetime.utcnow(),
            "readBy": [],
        }
        
        doc_ref = self.db.collection(COLLECTIONS["notifications"]).add(notification_data)
        return doc_ref[1].id
    
    async def get_notifications_for_location(
        self, 
        state: str = None, 
        district: str = None,
        limit: int = 20
    ) -> List[dict]:
        """Get notifications for a location."""
        if not self.db:
            return []
        
        query = self.db.collection(COLLECTIONS["notifications"])
        
        if state:
            query = query.where("state", "==", state)
        if district:
            query = query.where("district", "==", district)
        
        query = query.order_by("createdAt", direction="DESCENDING").limit(limit)
        
        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    
    async def mark_notification_read(self, notification_id: str, user_id: str):
        """Mark a notification as read by a user."""
        if not self.db:
            return
        
        from google.cloud.firestore import ArrayUnion
        self.db.collection(COLLECTIONS["notifications"]).document(notification_id).update({
            "readBy": ArrayUnion([user_id])
        })
    
    # ==================== VILLAGE AGGREGATION (For Sarpanch) ====================
    
    async def get_village_stats(self, state: str, district: str) -> dict:
        """
        Get aggregated stats for a village (for Sarpanch dashboard).
        """
        if not self.db:
            return {
                "total_farmers": 0,
                "total_farms": 0,
                "predictions_today": 0,
            }
        
        # Count farmers in location
        farmers = await self.get_users_by_location(state=state, district=district)
        farmer_count = len([u for u in farmers if u.get("role") == "farmer"])
        
        # Count farms
        farm_count = 0
        for farmer in farmers:
            farms = await self.get_farms_for_user(farmer["uid"])
            farm_count += len(farms)
        
        # Count today's predictions
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        prediction_query = (
            self.db.collection(COLLECTIONS["predictions"])
            .where("timestamp", ">=", today)
        )
        predictions_today = len(list(prediction_query.stream()))
        
        return {
            "total_farmers": farmer_count,
            "total_farms": farm_count,
            "predictions_today": predictions_today,
        }


# Singleton instance
_db_service = None

def get_db_service() -> DatabaseService:
    """Get singleton database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
