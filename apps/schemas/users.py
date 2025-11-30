from pydantic import BaseModel
from typing import Optional
from enum import Enum

# Define valid roles to prevent typos
class UserRole(str, Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    ADMIN = "admin"

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    # Default to customer if not sent
    role: UserRole = UserRole.CUSTOMER 

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str  # Send role back to Flutter
    
    class Config:
        from_attributes = True