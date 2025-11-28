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
@router.post("/place", response_model=schemas.OrderResponse)
async def place_order(
    order: schemas.OrderCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(database.get_db),
    # Optional: Require login to place order?
    # current_user: models.UserDB = Depends(auth.get_current_user) 
):
    new_order = models.OrderDB(
        item_name=order.item_name,
        quantity=order.quantity,
        customer_id=order.customer_id,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    background_tasks.add_task(simulate_cooking, new_order.id)
    return new_order

@router.get("/{order_id}", response_model=schemas.OrderResponse)
async def get_order(order_id: int, db: Session = Depends(database.get_db)):
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order