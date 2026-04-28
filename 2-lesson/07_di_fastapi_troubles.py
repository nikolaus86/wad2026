from fastapi import FastAPI
import uvicorn
from fastapi import APIRouter, Depends
from time import time
from typing import Protocol
import random

class DatabaseProto(Protocol):
    async def get_all(self):
        pass

class Dict(DatabaseProto):
    def __init__(self):
        self.items = [i for i in range(10)]

    async def get_all(self):
        return self.items

class CacheProto(Protocol):
    def get(self, key: str):
        pass

class ObjectCache(CacheProto):
    def __init__(self):
        if random.random() > 0.5:
            self.data = {
                "items": [i for i in range(10)]
            }
        else:
            self.data = None
    
    def get(self, key: str):
        return self.data[key] if self.data else None


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

def cache():
    return ObjectCache()

app = FastAPI()
router = APIRouter()

async def multiple_service(db: DatabaseProto):
    res = []
    data = await db.get_all()
    for i in data:
        res.append(i * 2)
    return res

async def multiply_by_api(data: list):
    res = []
    for i in data:
        res.append(i * 3)
    return res

async def service(db: DatabaseProto):
    data = await multiple_service(db)
    return await multiply_by_api(data)


@router.get("/items")
async def get_items(
    db: DatabaseProto = Depends(Database()), 
    cache: CacheProto = Depends(cache)
    ):
    cached_items = cache.get("items")
    if cached_items is None:
        data = await service(db)
        return data
    return cached_items

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)