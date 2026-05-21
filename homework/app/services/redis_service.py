import json
from datetime import datetime, timezone

from redis.asyncio import Redis

from app.core.config import get_settings


def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


class RefreshSessionService:
    def __init__(self, redis: Redis | None = None):
        self.settings = get_settings()
        self.redis = redis or get_redis()

    def _key(self, token: str) -> str:
        return f"refresh:{token}"

    async def save(self, token: str, user_id: int, login: str) -> None:
        payload = {
            "user_id": user_id,
            "login": login,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        ttl_seconds = self.settings.refresh_ttl_days * 24 * 60 * 60
        await self.redis.setex(self._key(token), ttl_seconds, json.dumps(payload))

    async def get(self, token: str) -> dict | None:
        raw = await self.redis.get(self._key(token))
        if not raw:
            return None
        return json.loads(raw)

    async def delete(self, token: str) -> None:
        await self.redis.delete(self._key(token))
