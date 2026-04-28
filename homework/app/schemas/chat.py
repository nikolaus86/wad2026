from datetime import datetime
from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    title: str = Field(default="New chat", max_length=120)


class ChatOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
