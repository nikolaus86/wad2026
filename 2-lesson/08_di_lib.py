from fastapi import FastAPI
import uvicorn
from fastapi import APIRouter, Depends
from time import time
from typing import Protocol
import random
from dependency-injector import containers, providers
from dependency-injector.wiring import Provide, inject

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


class Container(containers.DeclarativeContainer):
    database = providers.Factory(Dict)
    cache = providers.Factory(ObjectCache)

container = Container()

app = FastAPI()
router = APIRouter()

async def multiple_service(database: DatabaseProto):
    res = []
    data = await database.get_all()
    for i in data:
        res.append(i * 2)
    return res

async def multiply_by_api(data: list):
    res = []
    for i in data:
        res.append(i * 3)
    return res

async def service():
    data = await multiple_service()
    return await multiply_by_api(data)


@router.get("/items")
@inject
async def get_items(
    database: DatabaseProto = Depends(Provide[Container.database]),
    cache: CacheProto = Depends(Provide[Container.cache])
    ):
    cached_items = cache.get("items")
    if cached_items is None:
        data = await service()
        return data
    return cached_items

app.include_router(router)

app.container = container
container.wire(modules=[__name__])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)