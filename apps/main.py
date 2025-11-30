from fastapi import FastAPI
from . import models, database
from .routers import users, orders, restaurants, chat # Import 'chat'

# Create all tables (Including the new ChatMessageDB)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="UrbanPlate Modular API")

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(restaurants.router)
app.include_router(chat.router) # Plug in the Chat

@app.get("/")
def root():
    return {"message": "UrbanPlate Backend is Running properly!"}