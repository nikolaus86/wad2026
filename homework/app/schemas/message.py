from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatWithMessages(BaseModel):
    id: int
    title: str
    messages: list[MessageOut]

    model_config = {"from_attributes": True}


class AskResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
