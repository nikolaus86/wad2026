from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatOut
from app.schemas.message import AskResponse, ChatWithMessages, MessageCreate
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["chats"])


@router.get("/chats", response_model=list[ChatOut])
async def list_chats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ChatService(db).list_chats(current_user.id)


@router.post("/chats", response_model=ChatOut, status_code=status.HTTP_201_CREATED)
async def create_chat(payload: ChatCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ChatService(db).create_chat(current_user.id, payload.title)


@router.get("/chats/{chat_id}", response_model=ChatWithMessages)
async def get_chat(chat_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await ChatService(db).get_chat(current_user.id, chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/chats/{chat_id}/messages", response_model=AskResponse)
async def ask(chat_id: int, payload: MessageCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await ChatService(db).ask(current_user.id, chat_id, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await ChatService(db).delete_chat(current_user.id, chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
