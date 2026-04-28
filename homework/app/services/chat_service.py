from sqlalchemy.orm import Session, joinedload

from app.models.chat import Chat
from app.models.message import Message
from app.services.llm_service import LLMService


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMService()

    def list_chats(self, user_id: int) -> list[Chat]:
        return (
            self.db.query(Chat)
            .filter(Chat.owner_id == user_id)
            .order_by(Chat.updated_at.desc())
            .all()
        )

    def create_chat(self, user_id: int, title: str = "New chat") -> Chat:
        chat = Chat(owner_id=user_id, title=title or "New chat")
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_chat(self, user_id: int, chat_id: int) -> Chat:
        chat = (
            self.db.query(Chat)
            .options(joinedload(Chat.messages))
            .filter(Chat.id == chat_id, Chat.owner_id == user_id)
            .first()
        )
        if not chat:
            raise ValueError("Chat not found")
        return chat

    def delete_chat(self, user_id: int, chat_id: int) -> None:
        chat = self.get_chat(user_id, chat_id)
        self.db.delete(chat)
        self.db.commit()

    def ask(self, user_id: int, chat_id: int, content: str) -> tuple[Message, Message]:
        chat = self.get_chat(user_id, chat_id)
        if chat.title == "New chat":
            chat.title = content[:70]

        user_msg = Message(chat_id=chat.id, role="user", content=content)
        self.db.add(user_msg)
        self.db.flush()

        answer = self.llm.answer(content)
        assistant_msg = Message(chat_id=chat.id, role="assistant", content=answer)
        self.db.add(assistant_msg)
        self.db.commit()
        self.db.refresh(user_msg)
        self.db.refresh(assistant_msg)
        return user_msg, assistant_msg
