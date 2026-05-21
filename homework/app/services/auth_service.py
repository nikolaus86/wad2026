from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User
from app.services.github_oauth_service import GitHubOAuthService
from app.services.redis_service import RefreshSessionService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.refresh_sessions = RefreshSessionService()
        self.github_oauth = GitHubOAuthService(db)

    async def register(self, login: str, password: str) -> User:
        if await self._get_by_login(login):
            raise ValueError("Login already exists")

        user = User(login=login, password_hash=hash_password(password))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def register_and_issue_tokens(self, login: str, password: str) -> dict[str, str]:
        user = await self.register(login, password)
        return await self.issue_tokens(user)

    async def login(self, login: str, password: str) -> dict[str, str]:
        user = await self.authenticate(login, password)
        return await self.issue_tokens(user)

    async def authenticate(self, login: str, password: str) -> User:
        user = await self._get_by_login(login)
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise ValueError("Invalid login or password")
        return user

    async def issue_tokens(self, user: User) -> dict[str, str]:
        access = create_access_token(str(user.id), {"login": user.login})
        refresh = create_refresh_token()
        await self.refresh_sessions.save(refresh, user.id, user.login)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    async def refresh(self, refresh_token: str) -> dict[str, str]:
        session = await self.refresh_sessions.get(refresh_token)
        if not session:
            raise ValueError("Invalid or expired refresh token")

        user = await self.db.get(User, int(session["user_id"]))
        if not user:
            await self.refresh_sessions.delete(refresh_token)
            raise ValueError("User not found")

        await self.refresh_sessions.delete(refresh_token)
        return await self.issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        await self.refresh_sessions.delete(refresh_token)

    def build_github_login_url(self) -> tuple[str, str]:
        return self.github_oauth.build_login_url()

    async def login_with_github(self, code: str, state: str, expected_state: str | None) -> dict[str, str]:
        if not expected_state or expected_state != state:
            raise ValueError("Invalid OAuth state")

        profile = await self.github_oauth.exchange_code(code)
        user = await self.github_oauth.get_or_create_user(profile)
        return await self.issue_tokens(user)

    async def _get_by_login(self, login: str) -> User | None:
        result = await self.db.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
