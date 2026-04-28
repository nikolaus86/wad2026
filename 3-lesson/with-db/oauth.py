from fastapi import FastAPI, APIRouter, Depends
from models import User, TokenPayload
from storage import User as DBUser
from security import TOKEN_LIFETIME, TOKEN_SECRET, TOKEN_ALGORITHM, validate_credentials
from datetime import datetime, timezone, timedelta
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from models import AccessToken
from depends import get_oauth_user, get_oauth_admin
from database import SessionDep, get_db_session
from sqlalchemy import select
from fastapi import status, HTTPException
import jwt
from utils import hash_password

app = FastAPI()
router = APIRouter()


def create_access_token(username: str, is_admin: bool, is_active: bool, id: int) -> str:
    payload = TokenPayload(
        username=username,
        is_admin=is_admin,
        is_active=is_active,
        id=id,
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFETIME)
    )
    return jwt.encode(jsonable_encoder(payload), TOKEN_SECRET, algorithm=TOKEN_ALGORITHM)

@router.post("/token")
async def init_session(db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> AccessToken:
    result = await db.execute(select(DBUser).where(DBUser.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not validate_credentials(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(username=user.username, is_admin=user.is_admin, is_active=user.is_active, id=user.id)
    return AccessToken(value=token)

@router.get("/me")
async def get_current_user(user: Annotated[User, Depends(get_oauth_user)]) -> User:
    return user

@router.get("/admin")
async def get_admin_user(user: Annotated[User, Depends(get_oauth_admin)]) -> User:
    return user

@router.post("/register")
async def register_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep) -> User:
    existing_user = await db.execute(select(DBUser).where(DBUser.username == form_data.username))
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    db_user = DBUser(username=form_data.username, password=hash_password(form_data.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return User(
        id=db_user.id,
        username=db_user.username,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin
    )

app.include_router(router)