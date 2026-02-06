from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from ..schemas import UserRead, DataCreate, DataItem, UserCreatePublic
from ..models import User, UserData
from ..utils import get_db

router = APIRouter(prefix="/users", tags=["users"]) 

@router.post("/", response_model=UserRead)
def create_or_update_user(user_in: UserCreatePublic, db: Session = Depends(get_db)):
    # If email provided, try to update existing user by email, otherwise create a new user
    user = None
    if user_in.email:
        user = db.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        # update fields
        if user_in.full_name is not None:
            user.full_name = user_in.full_name
        if user_in.phone is not None:
            user.phone = user_in.phone
        if user_in.location is not None:
            user.location = user_in.location
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    # create new user
    new_user = User(email=user_in.email, full_name=user_in.full_name, phone=user_in.phone, location=user_in.location)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=UserRead)
def get_user(id: Optional[int] = Query(None), email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if id is None and email is None:
        raise HTTPException(status_code=400, detail="Provide `id` or `email` to find a user")
    if id is not None:
        user = db.get(User, id)
    else:
        user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/{user_id}/data", response_model=DataItem)
def create_user_data(user_id: int, item: DataCreate, db: Session = Depends(get_db)):
    # ensure user exists
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = UserData(user_id=user_id, key=item.key, value=item.value)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

@router.get("/{user_id}/data", response_model=List[DataItem])
def get_user_data(user_id: int, db: Session = Depends(get_db)):
    statement = select(UserData).where(UserData.user_id == user_id)
    results = db.exec(statement).all()
    return results
