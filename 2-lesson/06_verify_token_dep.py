from fastapi import FastAPI
import uvicorn
from fastapi import APIRouter, Depends
from time import time
from typing import Protocol
from fastapi import Header, HTTPException

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

async def verify_token(token: str = Header()) -> bool:
    if token != "123":
        raise HTTPException(status_code=401)
    return True


app = FastAPI(dependencies=[Depends(verify_token)])
router = APIRouter()

@router.get("/items")
async def get_items(
    db: DatabaseProto = Depends(Database()),
    is_valid: bool = Depends(verify_token)
):
    print(is_valid)
    return await db.get_all()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)