from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
# .. means go up one level to access models/schemas
from .. import models, schemas, database, auth 

router = APIRouter(prefix="/users", tags=["Authentication & Users"])

# 1. REGISTER USER (Now with Role support)
@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Check if user exists
    db_user = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Create new user with HASHED password and ROLE
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.UserDB(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_pwd,
        role=user.role # This comes from the Schema (defaults to "customer")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 3. Return the user object
    # The Schema (UserResponse) will filter out the password and include the role
    return new_user

# 2. LOGIN (Returns Token)
@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Find User
    user = db.query(models.UserDB).filter(models.UserDB.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # 2. Check Password
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # 3. Return Token
    # We can also add "role": user.role to the token data if we want
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 3. GET MY PROFILE
@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.UserDB = Depends(auth.get_current_user)):
    return current_user

# 4. UPDATE MY PROFILE
@router.patch("/me", response_model=schemas.UserResponse)
async def update_user_me(
    updates: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.UserDB = Depends(auth.get_current_user)
):
    # A. Check Email Uniqueness (If they are changing email)
    if updates.email and updates.email != current_user.email:
        existing_email = db.query(models.UserDB).filter(models.UserDB.email == updates.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already currently in use")
            
    # B. Check Username Uniqueness
    if updates.username and updates.username != current_user.username:
        existing_user = db.query(models.UserDB).filter(models.UserDB.username == updates.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

    # C. Apply Updates
    update_data = updates.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        # SECURITY CRITICAL: If updating password, Hash it first!
        if key == "password":
            hashed_value = auth.get_password_hash(value)
            setattr(current_user, "hashed_password", hashed_value)
        else:
            setattr(current_user, key, value)
            
    db.commit()
    db.refresh(current_user)
    return current_user