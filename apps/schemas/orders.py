from pydantic import BaseModel
from enum import Enum

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