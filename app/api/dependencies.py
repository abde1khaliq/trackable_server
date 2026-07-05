from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.jwt import jwt_handler

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt_handler.verify_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
