from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.controllers import auth, chats, ui
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(ui.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
