from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User
from app.services.redis_service import RefreshSessionService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.refresh_sessions = RefreshSessionService()

    def register(self, login: str, password: str) -> User:
        existing = self.db.query(User).filter(User.login == login).first()
        if existing:
            raise ValueError("Login already exists")
        user = User(login=login, password_hash=hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, login: str, password: str) -> User:
        user = self.db.query(User).filter(User.login == login).first()
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise ValueError("Invalid login or password")
        return user

    def issue_tokens(self, user: User) -> dict[str, str]:
        access = create_access_token(str(user.id), {"login": user.login})
        refresh = create_refresh_token()
        self.refresh_sessions.save(refresh, user.id, user.login)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    def refresh(self, refresh_token: str) -> dict[str, str]:
        session = self.refresh_sessions.get(refresh_token)
        if not session:
            raise ValueError("Invalid or expired refresh token")
        user = self.db.get(User, int(session["user_id"]))
        if not user:
            self.refresh_sessions.delete(refresh_token)
            raise ValueError("User not found")
        self.refresh_sessions.delete(refresh_token)
        return self.issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        self.refresh_sessions.delete(refresh_token)
