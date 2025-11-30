from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth

router = APIRouter(prefix="/restaurants", tags=["Restaurant Admin"])

# 1. CREATE RESTAURANT (User becomes Owner)
@router.post("/", response_model=schemas.RestaurantResponse)
async def create_restaurant(
    restaurant: schemas.RestaurantCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    new_restaurant = models.RestaurantDB(
        name=restaurant.name,
        cuisine_type=restaurant.cuisine_type,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
        owner_id=current_user.id, # Link to the logged-in user
        is_open=True
    )
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    return new_restaurant

# 2. UPDATE RESTAURANT (Only Owner can do this)
@router.patch("/{restaurant_id}", response_model=schemas.RestaurantResponse)
async def update_restaurant(
    restaurant_id: int,
    updates: schemas.RestaurantUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    # Find Restaurant
    r_db = db.query(models.RestaurantDB).filter(models.RestaurantDB.id == restaurant_id).first()
    if not r_db:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Check Ownership
    if r_db.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this restaurant")
    
    # Apply Updates
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(r_db, key, value)
        
    db.commit()
    db.refresh(r_db)
    return r_db

# 3. DELETE RESTAURANT (Only Owner)
@router.delete("/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    r_db = db.query(models.RestaurantDB).filter(models.RestaurantDB.id == restaurant_id).first()
    if not r_db:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if r_db.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this restaurant")
    
    db.delete(r_db)
    db.commit()
    return {"message": "Restaurant deleted successfully"}

# 4. ADD MENU ITEM (Cuisines/Dishes)
@router.post("/{restaurant_id}/menu", response_model=schemas.MenuItemResponse)
async def add_menu_item(
    restaurant_id: int,
    item: schemas.MenuItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    # Verify Restaurant and Owner
    r_db = db.query(models.RestaurantDB).filter(models.RestaurantDB.id == restaurant_id).first()
    if not r_db:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if r_db.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can add items")
        
    new_item = models.MenuItemDB(
        name=item.name,
        description=item.description,
        price=item.price,
        restaurant_id=restaurant_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Return with restaurant name
    return schemas.MenuItemResponse(
        id=new_item.id,
        name=new_item.name,
        description=new_item.description,
        price=new_item.price,
        restaurant_name=r_db.name
    )

# 6. UPDATE MENU ITEM (Price, Name, Desc)
@router.patch("/menu/{item_id}", response_model=schemas.MenuItemResponse)
async def update_menu_item(
    item_id: int,
    updates: schemas.MenuItemUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    # 1. Find the Item
    item_db = db.query(models.MenuItemDB).filter(models.MenuItemDB.id == item_id).first()
    if not item_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # 2. Security Check: Does the current user own the restaurant this item belongs to?
    # We access the relationship 'item_db.restaurant' to check the owner_id
    if item_db.restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this item")
    
    # 3. Apply Updates
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item_db, key, value)
        
    db.commit()
    db.refresh(item_db)
    
    # 4. Return formatted response (we need restaurant name for the schema)
    return schemas.MenuItemResponse(
        id=item_db.id,
        name=item_db.name,
        description=item_db.description,
        price=item_db.price,
        restaurant_name=item_db.restaurant.name
    )

# 7. DELETE MENU ITEM
@router.delete("/menu/{item_id}")
async def delete_menu_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    # 1. Find the Item
    item_db = db.query(models.MenuItemDB).filter(models.MenuItemDB.id == item_id).first()
    if not item_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # 2. Security Check
    if item_db.restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")
    
    # 3. Delete
    db.delete(item_db)
    db.commit()
    
    return {"message": "Menu item deleted successfully"}

# 5. PUBLIC: GET ALL MENU ITEMS (Feed for Users)
@router.get("/menu/all", response_model=List[schemas.MenuItemResponse])
async def get_all_menu_items(db: Session = Depends(database.get_db)):
    # Join tables to get restaurant name easily
    items = db.query(models.MenuItemDB).all()
    
    response_list = []
    for i in items:
        # We fetch the parent restaurant to get the name
        r_name = i.restaurant.name if i.restaurant else "Unknown"
        response_list.append(
            schemas.MenuItemResponse(
                id=i.id, name=i.name, description=i.description, 
                price=i.price, restaurant_name=r_name
            )
        )
    return response_list