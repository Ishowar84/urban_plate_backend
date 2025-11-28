from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# --- AUTH SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- MENU ITEM SCHEMAS (New) ---
class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float

class MenuItemResponse(MenuItemCreate):
    id: int
    restaurant_name: Optional[str] = None 
    class Config:
        from_attributes = True

# --- RESTAURANT SCHEMAS (Updated) ---
class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: str
    latitude: float
    longitude: float

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    cuisine_type: Optional[str] = None
    is_open: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RestaurantResponse(RestaurantCreate):
    id: int
    is_open: bool
    rating: float
    owner_id: int
    # This list allows us to see the menu when we fetch a restaurant
    menu_items: List[MenuItemResponse] = [] 
    
    class Config:
        from_attributes = True

# --- ORDER SCHEMAS ---
class OrderStatus(str, Enum):
    PENDING = "pending"
    COOKING = "cooking"
    READY = "ready"

class OrderCreate(BaseModel):
    item_name: str
    quantity: int
    customer_id: int

class OrderResponse(OrderCreate):
    id: int
    status: str
    class Config:
        from_attributes = True

# --- USER LOCATION SCHEMAS ---
class UserLocation(BaseModel):
    address_label: str
    address_text: str
    latitude: float
    longitude: float
    class Config:
        from_attributes = True

class UserLocationUpdate(BaseModel):
    address_label: Optional[str] = None
    address_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None