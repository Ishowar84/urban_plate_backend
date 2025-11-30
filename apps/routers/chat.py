from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from jose import jwt, JWTError
from .. import models, database, schemas, auth

router = APIRouter(prefix="/chat", tags=["Order Chat"])

# --- WEBSOCKET MANAGER ---
class ChatManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, order_id: int):
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append(websocket)

    def disconnect(self, websocket: WebSocket, order_id: int):
        if order_id in self.active_connections:
            if websocket in self.active_connections[order_id]:
                self.active_connections[order_id].remove(websocket)

    async def broadcast(self, message: dict, order_id: int):
        if order_id in self.active_connections:
            for connection in self.active_connections[order_id]:
                await connection.send_json(message)

manager = ChatManager()

# --- SECURITY HELPER FOR WEBSOCKETS ---
async def get_user_from_socket(token: str, db: Session):
    """
    Manually decode JWT for WebSockets since they can't use the Header dependency
    """
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
        
    user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    return user

# --- ENDPOINTS ---

# 1. GET CHAT HISTORY (SECURE)
@router.get("/{order_id}/history", response_model=List[schemas.ChatMessageResponse])
async def get_chat_history(
    order_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # AUTH CHECK: Only the Customer (or Admin/Restaurant Owner) can see this
    # Note: We need to link Orders to Restaurants properly to check Owner ID
    # For now, we enforce Customer ID check:
    if order.customer_id != current_user.id:
        # In a real app, also check: or current_user.id == order.restaurant.owner_id
        raise HTTPException(status_code=403, detail="Not authorized to view this chat")

    if order.status in ["delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Chat is closed")
        
    return db.query(models.ChatMessageDB).filter(models.ChatMessageDB.order_id == order_id).all()

# 2. SEND MESSAGE (HTTP POST) - SECURE
@router.post("/{order_id}/{sender_type}/send", response_model=schemas.ChatMessageResponse)
async def send_message(
    order_id: int, 
    sender_type: str, 
    chat_data: schemas.ChatMessageCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # AUTH CHECK
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if order.status in ["delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Chat is closed")

    # Save
    timestamp = datetime.now().isoformat()
    new_msg = models.ChatMessageDB(
        order_id=order_id,
        sender_type=sender_type,
        message=chat_data.message,
        timestamp=timestamp
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    # Broadcast
    response_data = {
        "sender_type": sender_type,
        "message": chat_data.message,
        "timestamp": timestamp
    }
    await manager.broadcast(response_data, order_id)
    
    return new_msg

# 3. WEBSOCKET - SECURE (Using Query Param for Token)
@router.websocket("/ws/{order_id}/{sender_type}")
async def websocket_endpoint(
    websocket: WebSocket, 
    order_id: int, 
    sender_type: str, 
    token: str = Query(...), # Expect ?token=... in URL
    db: Session = Depends(database.get_db)
):
    # 1. Manually Validate Token
    user = await get_user_from_socket(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Validate Order & Ownership
    order = db.query(models.OrderDB).filter(models.OrderDB.id == order_id).first()
    if not order:
        await websocket.close(code=1000)
        return
        
    # AUTH CHECK: Ensure the connected user is the one on the order
    if order.customer_id != user.id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if order.status in ["delivered", "cancelled"]:
        await websocket.close(code=1000)
        return

    # 3. Connect
    await manager.connect(websocket, order_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            timestamp = datetime.now().isoformat()
            new_msg = models.ChatMessageDB(
                order_id=order_id,
                sender_type=sender_type,
                message=data,
                timestamp=timestamp
            )
            db.add(new_msg)
            db.commit()
            
            response_data = {
                "sender_type": sender_type,
                "message": data,
                "timestamp": timestamp
            }
            await manager.broadcast(response_data, order_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, order_id)

# 4. EDIT MESSAGE (SECURE)
@router.patch("/message/{message_id}")
async def edit_message(
    message_id: int, 
    update_data: schemas.ChatMessageUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    msg = db.query(models.ChatMessageDB).filter(models.ChatMessageDB.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    # Ensure user owns the order related to this message
    if msg.order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    msg.message = update_data.message
    db.commit()
    
    socket_payload = {
        "event": "edit",
        "message_id": message_id,
        "new_message": msg.message,
        "timestamp": msg.timestamp
    }
    await manager.broadcast(socket_payload, msg.order_id)
    return {"status": "updated", "message": msg.message}

# 5. DELETE MESSAGE (SECURE)
@router.delete("/message/{message_id}")
async def delete_message(
    message_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    msg = db.query(models.ChatMessageDB).filter(models.ChatMessageDB.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    if msg.order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    order_id = msg.order_id
    db.delete(msg)
    db.commit()
    
    socket_payload = {"event": "delete", "message_id": message_id}
    await manager.broadcast(socket_payload, order_id)
    return {"status": "deleted"}