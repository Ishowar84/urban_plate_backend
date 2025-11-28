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
    
    # Relationship: One user can own multiple restaurants
    restaurants = relationship("RestaurantDB", back_populates="owner")

# --- BUSINESS TABLES ---
class RestaurantDB(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cuisine_type = Column(String) # e.g. "Italian", "Nepali"
    rating = Column(Float, default=0.0)
    is_open = Column(Boolean, default=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Link to the User who owns this restaurant
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="restaurants")
    
    # Link to Menu Items
    menu_items = relationship("MenuItemDB", back_populates="restaurant")

class MenuItemDB(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # e.g. "Chicken Momo"
    description = Column(String)      # e.g. "Steamed with spices"
    price = Column(Float)             # e.g. 250.0
    
    # Link back to Restaurant
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    restaurant = relationship("RestaurantDB", back_populates="menu_items")

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String)
    quantity = Column(Integer)
    customer_id = Column(Integer)
    status = Column(String, default="pending") 

class UserLocationDB(Base):
    __tablename__ = "user_locations"
    user_id = Column(Integer, primary_key=True, index=True) 
    address_label = Column(String)
    address_text = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)