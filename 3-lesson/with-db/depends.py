from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from storage import User as DBUser
from security import TOKEN_SECRET, TOKEN_ALGORITHM
from database import SessionDep
from typing import Annotated
from sqlalchemy import select
import jwt

oauth = OAuth2PasswordBearer(tokenUrl="token")

async def get_oauth_user(
    token: Annotated[str, Depends(oauth)],
    session: SessionDep
) -> User | None:
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await session.execute(select(DBUser).where(DBUser.username == payload["username"]))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    return User(
        id=db_user.id,
        username=db_user.username,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin
    )

async def get_oauth_admin(
    user: Annotated[User, Depends(get_oauth_user)]
) -> User | None:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


    