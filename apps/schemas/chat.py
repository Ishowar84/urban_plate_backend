from pydantic import BaseModel

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    sender_type: str # "user" or "restaurant"
    message: str
    timestamp: str
    
    class Config:
        from_attributes = True

# Schema for Editing a message
class ChatMessageUpdate(BaseModel):
    message: str        