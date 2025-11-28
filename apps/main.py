from fastapi import FastAPI
from . import models, database
from .routers import users, orders, restaurants

# 1. Create all tables in the DB
models.Base.metadata.create_all(bind=database.engine)

# 2. Init App
app = FastAPI(title="UrbanPlate Modular API")

# 3. Include Routers (Plug in the appliances)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(restaurants.router)

@app.get("/")
def root():
    return {"message": "UrbanPlate Backend is Running properly!"}