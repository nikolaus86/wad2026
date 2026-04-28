from fastapi import FastAPI
import uvicorn
from fastapi import APIRouter, Depends
from time import time
from typing import Protocol

class DatabaseProto(Protocol):
    async def get_all(self):
        pass

    async def get_session(self):
        pass

class SessionProto(Protocol):
    async def execute(self):
        pass

    async def close(self):
        pass

class DictSession(SessionProto):
    def __init__(self, d: DatabaseProto):
        self.d = d

    async def execute(self):
        print("Execute session")
        return await self.d.get_all()

    async def close(self):
        print("Close session")



class Dict(DatabaseProto):
    def __init__(self):
        self.items = [i for i in range(10)]

    async def get_all(self):
        return self.items

    async def get_session(self) -> SessionProto:
        return DictSession(d=self)


class Database:
    def __init__(self):
        db = Dict()
        orig_get_all = db.get_all

        async def track():
            t = time()
            try:
                return await orig_get_all()
            finally:
                print(f"Time: {time() - t}")
        self.db = db
        self.db.get_all = track

    def __call__(self):
        return self.db


app = FastAPI()
router = APIRouter()
router1 = APIRouter()

@router.get("/items")
async def get_items(db: DatabaseProto = Depends(Database())):
    return await db.get_all()

async def session(db: DatabaseProto = Depends(Database())) -> SessionProto:
    s = await db.get_session()
    return s

@router1.get("/items-session")
async def get_items_session(session: SessionProto = Depends(session)):
    return await session.execute()

app.include_router(router)
app.include_router(router1)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)