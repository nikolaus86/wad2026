import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://user:admin@localhost:5432/webdev")
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 'Hello World'"))
        print(result.all())

asyncio.run(main())


