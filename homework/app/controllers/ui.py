from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.dependencies import get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.services.chat_service import ChatService
from app.services.ui_service import UIService

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/templates")


def get_ui_service(db: AsyncSession) -> UIService:
    return UIService(ChatService(db))


@router.get("/")
async def index(request: Request, user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    context = await get_ui_service(db).get_index_context(user)
    if not context:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("index.html", {"request": request, **context})


@router.get("/login")
async def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/ui/chats")
async def create_chat_ui(title: str = Form("New chat"), user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    chat = await get_ui_service(db).create_chat(user, title)
    if not chat:
        return RedirectResponse("/login", status_code=303)

    return RedirectResponse(f"/chats/{chat.id}", status_code=303)


@router.get("/chats/{chat_id}")
async def chat_page(request: Request, chat_id: int, user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    context = await get_ui_service(db).get_chat_page_context(user, chat_id)
    if not context:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("chat.html", {"request": request, **context})
