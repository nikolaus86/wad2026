from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from security import TOKEN_SECRET, TOKEN_ALGORITHM
from storage import users_storage
from typing import Annotated
import jwt

oauth = OAuth2PasswordBearer(tokenUrl="token")

async def get_oauth_user(
    token: Annotated[str, Depends(oauth)]
) -> User | None:
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = users_storage.get(payload["username"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    return user

async def get_oauth_admin(
    user: Annotated[User, Depends(get_oauth_user)]
) -> User | None:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


    