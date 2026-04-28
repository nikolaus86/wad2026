from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.controllers.dependencies import get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.services.chat_service import ChatService

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def index(request: Request, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login", status_code=303)
    chats = ChatService(db).list_chats(user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "chats": chats})


@router.get("/login")
def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/ui/chats")
def create_chat_ui(title: str = Form("New chat"), user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login", status_code=303)
    chat = ChatService(db).create_chat(user.id, title)
    return RedirectResponse(f"/chats/{chat.id}", status_code=303)


@router.get("/chats/{chat_id}")
def chat_page(request: Request, chat_id: int, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login", status_code=303)
    service = ChatService(db)
    try:
        chat = service.get_chat(user.id, chat_id)
    except ValueError:
        return RedirectResponse("/", status_code=303)
    chats = service.list_chats(user.id)
    return templates.TemplateResponse("chat.html", {"request": request, "user": user, "chat": chat, "chats": chats})
