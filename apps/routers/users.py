from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
# .. means go up one level to access models/schemas
from .. import models, schemas, database, auth 

router = APIRouter(prefix="/users", tags=["Authentication"])

@router.post("/register", response_model=schemas.Token)
async def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Check if user exists
    db_user = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Create new user with HASHED password
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.UserDB(username=user.username, email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    
    # 3. Create Token (Auto-login)
    access_token = auth.create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Find User
    user = db.query(models.UserDB).filter(models.UserDB.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 2. Check Password
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 3. Return Token
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: models.UserDB = Depends(auth.get_current_user)):
    return {"username": current_user.username, "id": current_user.id, "email": current_user.email}