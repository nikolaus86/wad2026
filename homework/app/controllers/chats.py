from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatOut
from app.schemas.message import AskResponse, ChatWithMessages, MessageCreate
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["chats"])


@router.get("/chats", response_model=list[ChatOut])
def list_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChatService(db).list_chats(current_user.id)


@router.post("/chats", response_model=ChatOut, status_code=status.HTTP_201_CREATED)
def create_chat(payload: ChatCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChatService(db).create_chat(current_user.id, payload.title)


@router.get("/chats/{chat_id}", response_model=ChatWithMessages)
def get_chat(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return ChatService(db).get_chat(current_user.id, chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/chats/{chat_id}/messages", response_model=AskResponse)
def ask(chat_id: int, payload: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_message, assistant_message = ChatService(db).ask(current_user.id, chat_id, payload.content)
        return {"user_message": user_message, "assistant_message": assistant_message}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        ChatService(db).delete_chat(current_user.id, chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
