from pydantic import BaseModel
from typing import Optional

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