from pydantic import BaseModel, Field, field_serializer
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

class User(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    username: str
    is_active: bool = True
    is_admin: bool = False


class AccessToken(BaseModel):
    value: str
    type: str = "Bearer"

class TokenPayload(User):
    iat: datetime
    exp: datetime

    @field_serializer("iat", "exp", when_used="json")
    def to_timestamp(self, value: datetime) -> datetime:
        return datetime.timestamp(value.replace(microsecond=0))

