from app.models.chat import Chat
from app.models.user import User
from app.services.chat_service import ChatService


class UIService:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def get_index_context(self, user: User | None) -> dict | None:
        if not user:
            return None
        chats = await self.chat_service.list_chats(user.id)
        return {"user": user, "chats": chats}

    async def create_chat(self, user: User | None, title: str) -> Chat | None:
        if not user:
            return None
        return await self.chat_service.create_chat(user.id, title)

    async def get_chat_page_context(self, user: User | None, chat_id: int) -> dict | None:
        if not user:
            return None

        try:
            chat = await self.chat_service.get_chat(user.id, chat_id)
        except ValueError:
            return None

        chats = await self.chat_service.list_chats(user.id)
        return {"user": user, "chat": chat, "chats": chats}
