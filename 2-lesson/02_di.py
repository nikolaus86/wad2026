from fastapi import FastAPI
import uvicorn
from fastapi import APIRouter, Depends
from time import time
from typing import Protocol

class DatabaseProto(Protocol):
    async def get_all(self):
        pass

class Dict(DatabaseProto):
    def __init__(self):
        self.items = [i for i in range(10)]

    async def get_all(self):
        return self.items


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

@router.get("/items")
async def get_items(db: DatabaseProto = Depends(Database())):
    return await db.get_all()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)