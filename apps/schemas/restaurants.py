from pydantic import BaseModel
from typing import List, Optional

# --- MENU ITEMS ---
class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class MenuItemResponse(MenuItemCreate):
    id: int
    restaurant_name: Optional[str] = None 
    class Config:
        from_attributes = True

# --- RESTAURANTS ---
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
    menu_items: List[MenuItemResponse] = [] 
    class Config:
        from_attributes = True