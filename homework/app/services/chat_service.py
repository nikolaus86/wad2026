import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat
from app.models.message import Message
from app.services.llm_service import LLMService


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def list_chats(self, user_id: int) -> list[Chat]:
        result = await self.db.execute(
            select(Chat)
            .where(Chat.owner_id == user_id)
            .order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())

    async def create_chat(self, user_id: int, title: str = "New chat") -> Chat:
        chat = Chat(owner_id=user_id, title=title or "New chat")
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_chat(self, user_id: int, chat_id: int) -> Chat:
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.messages))
            .where(Chat.id == chat_id, Chat.owner_id == user_id)
        )
        chat = result.scalar_one_or_none()
        if not chat:
            raise ValueError("Chat not found")
        return chat

    async def delete_chat(self, user_id: int, chat_id: int) -> None:
        chat = await self.get_chat(user_id, chat_id)
        await self.db.delete(chat)
        await self.db.commit()

    async def ask(self, user_id: int, chat_id: int, content: str) -> dict[str, Message]:
        chat = await self.get_chat(user_id, chat_id)
        if chat.title == "New chat":
            chat.title = content[:70]

        user_msg = Message(chat_id=chat.id, role="user", content=content)
        self.db.add(user_msg)
        await self.db.flush()

        answer = await asyncio.to_thread(self.llm.answer, content)
        assistant_msg = Message(chat_id=chat.id, role="assistant", content=answer)
        self.db.add(assistant_msg)
        await self.db.commit()
        await self.db.refresh(user_msg)
        await self.db.refresh(assistant_msg)
        return {"user_message": user_msg, "assistant_message": assistant_msg}
