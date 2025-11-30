from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
import asyncio

router = APIRouter(prefix="/orders", tags=["Orders"])

# Simulation Logic
async def simulate_cooking(order_id: int):
    await asyncio.sleep(5)
    print(f"Order {order_id}: Cooking finished (Simulation)")

# Endpoints

# 1. PLACE ORDER (SECURE)
@router.post("/place", response_model=schemas.OrderResponse)
async def place_order(
    order: schemas.OrderCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user) # REQUIRE LOGIN
):
    # SECURITY FIX:
    # Instead of trusting the 'customer_id' from the JSON, 
    # we use the ID of the user who is actually logged in.
    real_customer_id = current_user.id
    
    new_order = models.OrderDB(
        item_name=order.item_name,
        quantity=order.quantity,
        customer_id=real_customer_id, # Locked to the token owner
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    background_tasks.add_task(simulate_cooking, new_order.id)
    return new_order

# 2. GET ORDER (SECURE)
@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def get_order(
    order_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user) # REQUIRE LOGIN
):
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # AUTH CHECK: Ensure the logged-in user actually owns this order
    # (In a real app, you would also allow the Restaurant Owner to view it)
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
        
    return order

# 3. UPDATE STATUS (SECURE)
@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
async def update_order_status(
    order_id: int, 
    status: schemas.OrderStatus, 
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user) # REQUIRE LOGIN
):
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the status
    order.status = status
    db.commit()
    db.refresh(order)
    
    # --- CHAT DELETION LOGIC ---
    # If the order is now closed, delete all chat messages
    if status in ["delivered", "cancelled"]: 
        db.query(models.ChatMessageDB).filter(models.ChatMessageDB.order_id == order_id).delete()
        db.commit()
        print(f"Chat history for Order {order_id} has been wiped.")
        
    return order