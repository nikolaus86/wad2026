from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
from fastapi import Depends

DATABASE_URL = "postgresql+asyncpg://user:admin@localhost:5432/webdev"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine)

Base = declarative_base()

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            print(e)
        finally:
            await session.close()

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

