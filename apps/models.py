from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# --- AUTH TABLE ---
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # NEW: Role Column
    role = Column(String, default="customer") # "customer", "restaurant", "admin"
    
    # Relationships
    restaurants = relationship("RestaurantDB", back_populates="owner")

# --- BUSINESS TABLES ---
class RestaurantDB(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cuisine_type = Column(String) 
    rating = Column(Float, default=0.0)
    is_open = Column(Boolean, default=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Link to Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="restaurants")
    
    # Link to Menu
    menu_items = relationship("MenuItemDB", back_populates="restaurant")

class MenuItemDB(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) 
    description = Column(String)      
    price = Column(Float)             
    
    # Link to Restaurant
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    restaurant = relationship("RestaurantDB", back_populates="menu_items")

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String)
    quantity = Column(Integer)
    customer_id = Column(Integer)
    status = Column(String, default="pending") 
    
    # Link to Chat
    chat_messages = relationship("ChatMessageDB", back_populates="order", cascade="all, delete")

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    sender_type = Column(String) # "user" or "restaurant"
    message = Column(String)
    timestamp = Column(String) 
    
    # Link to Order
    order = relationship("OrderDB", back_populates="chat_messages")

class UserLocationDB(Base):
    __tablename__ = "user_locations"
    user_id = Column(Integer, primary_key=True, index=True) 
    address_label = Column(String)
    address_text = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)