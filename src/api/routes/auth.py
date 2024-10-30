from fastapi import Request, HTTPException, Response, APIRouter
from schemas.auth import SignUpRequest, SignInRequest
from core.security import hash_password, verify_password, create_access_token
from utils.dbconnector import get_mongo_client
from dependencies.auth import get_current_user
from datetime import datetime
from models.user import User

router = APIRouter(prefix="/auth")

db = get_mongo_client()
collection = db['users']
    
async def async_find_one(input):
    return db.users.find_one(input)

async def async_insert_one(new_user):
    return db.users.insert_one(new_user)

@router.get("/cookie")
async def func(request: Request): 
    access_token = request.cookies.get("access_token")
    current_user = await get_current_user(access_token)  
    return {"access_token": access_token,
            "message": f"Welcome, user {current_user}" }

@router.post("/signup")
async def sign_up(signup_data: SignUpRequest):
    existing_user = await async_find_one({"email": signup_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(signup_data.password)
    
    new_user = User(email=signup_data.email, hashed_password=hashed_password, created_at=datetime.datetime.now(datetime.timezone.utc))
    result = await async_insert_one(new_user.model_dump())

    return {"message": "User created successfully", "user_id": str(result.inserted_id)}\

import datetime
@router.post("/signin")
async def sign_in(signin_data: SignInRequest, response: Response):

    user = await async_find_one({"email": signin_data.email})

    if not user or not verify_password(signin_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": str(user["_id"])}).decode('utf-8')
 
    response.set_cookie(key = "access_token", value=access_token, samesite="Lax", secure=False, httponly=True)
    
    return {"message": "Login successful",
            "key": access_token}
 
 
@router.post("/logout")      
def logout(response: Response):
    response.delete_cookie(key="access_token") 
    return {"message": "Logged out"}