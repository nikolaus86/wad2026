from sqlalchemy import MetaData, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional

metadata_obj = MetaData()

class Base(DeclarativeBase):
    metadata = metadata_obj

class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    fullname: Mapped[Optional[str]]
    nickname: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

