import secrets
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User


class GitHubOAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    def build_login_url(self) -> tuple[str, str]:
        if not self.settings.github_client_id:
            raise ValueError("GitHub OAuth is not configured")
        state = secrets.token_urlsafe(24)
        params = urlencode({
            "client_id": self.settings.github_client_id,
            "redirect_uri": self.settings.github_callback_url,
            "scope": "read:user user:email",
            "state": state,
        })
        return f"https://github.com/login/oauth/authorize?{params}", state

    async def exchange_code(self, code: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.settings.github_client_id,
                    "client_secret": self.settings.github_client_secret,
                    "code": code,
                    "redirect_uri": self.settings.github_callback_url,
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("GitHub did not return access token")

            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            )
            user_response.raise_for_status()
            return user_response.json()

    async def get_or_create_user(self, github_profile: dict) -> User:
        github_id = str(github_profile["id"])
        login = github_profile.get("login") or f"github_{github_id}"

        result = await self.db.execute(select(User).where(User.github_id == github_id))
        user = result.scalar_one_or_none()
        if user:
            return user

        base_login = login
        suffix = 1
        while await self._login_exists(login):
            suffix += 1
            login = f"{base_login}_{suffix}"

        user = User(login=login, github_id=github_id, password_hash=None)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def _login_exists(self, login: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.login == login).limit(1))
        return result.scalar_one_or_none() is not None
