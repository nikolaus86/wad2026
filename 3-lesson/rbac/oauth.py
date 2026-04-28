from fastapi import FastAPI, APIRouter, Request, Depends
from models import User, TokenPayload
from storage import users_storage
from security import TOKEN_LIFETIME, TOKEN_SECRET, TOKEN_ALGORITHM, validate_credentials
from datetime import datetime, timezone, timedelta
from fastapi.encoders import jsonable_encoder
import jwt
from fastapi import status, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from models import AccessToken
from depends import get_oauth_user, get_oauth_admin

app = FastAPI()
router = APIRouter()

def get_or_create_user(username: str) -> User:
    if username not in users_storage:
        users_storage[username] = User(username=username)
    return users_storage[username]

def create_access_token(username: str) -> str:
    payload = TokenPayload(
        username=username,
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFETIME)
    )
    return jwt.encode(jsonable_encoder(payload), TOKEN_SECRET, algorithm=TOKEN_ALGORITHM)

@router.post("/token")
async def init_session(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> AccessToken:
    if not validate_credentials(form_data.username, form_data.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    token = create_access_token(username=form_data.username)
    return AccessToken(value=token)

@router.get("/me")
async def get_current_user(user: Annotated[User, Depends(get_oauth_user)]) -> User:
    return user

@router.get("/admin")
async def get_admin_user(user: Annotated[User, Depends(get_oauth_admin)]) -> User:
    return user

app.include_router(router)