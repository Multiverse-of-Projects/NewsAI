from fastapi import HTTPException, status
from core.security import decode_access_token
from jwt import PyJWTError
from src.utils.dbconnector import get_mongo_client
from api.schemas.auth import GetUserResponse
db = get_mongo_client()
collection = db['users']

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(token) -> GetUserResponse:
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        
        return GetUserResponse(user_id=user_id)
    
    except PyJWTError:
        raise credentials_exception