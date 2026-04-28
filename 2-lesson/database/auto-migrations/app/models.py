from sqlalchemy import func, String, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

metadata_obj = MetaData()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

