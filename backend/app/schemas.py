from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Public user model (no password required)
class UserCreatePublic(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: Optional[EmailStr]
    full_name: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class DataCreate(BaseModel):
    key: str
    value: str

class DataItem(BaseModel):
    id: int
    user_id: int
    key: str
    value: str
    created_at: datetime

    model_config = {"from_attributes": True}
