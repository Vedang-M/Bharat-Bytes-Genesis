"""
Admin Routes
Endpoints for system administration, user management, and stats.
Protected by role='admin'.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from ..middleware.auth_middleware import require_role
from ..services.db_service import get_db_service

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/users")
async def list_users(
    limit: int = Query(50, ge=1, le=100),
    role: str = Depends(require_role("admin"))
):
    """
    List all users in the system.
    Requires 'admin' role.
    """
    try:
        db_service = get_db_service()
        users = await db_service.get_all_users(limit=limit)
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_system_stats(
    role: str = Depends(require_role("admin"))
):
    """
    Get high-level system statistics.
    Requires 'admin' role.
    """
    try:
        db_service = get_db_service()
        
        # Get simplified stats from users list
        # In production this should be optimized with aggregation queries
        users = await db_service.get_all_users(limit=1000)
        
        total_farmers = len([u for u in users if u.get("role") == "farmer"])
        total_sarpanch = len([u for u in users if u.get("role") == "sarpanch"])
        total_admins = len([u for u in users if u.get("role") == "admin"])
        
        # Mocking other stats since we don't have aggregation queries yet
        stats = {
            "users": {
                "total": len(users),
                "farmers": total_farmers,
                "sarpanch": total_sarpanch,
                "admins": total_admins
            },
            "system": {
                "active_alerts": 5,
                "total_predictions": 142,
                "crops_tracked": 12
            }
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
