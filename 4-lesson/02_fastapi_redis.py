from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis.asyncio as redis

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.on_event("shutdown")
async def shutdown_event():
    global redis_client
    await redis_client.aclose()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    cached_item = await redis_client.get(f"item:{item_id}")
    if cached_item:
        return JSONResponse(content={"item_id": item_id, "data": cached_item, "cached": True})
    
    data = f"This is item {item_id}"

    await redis_client.set(f"item:{item_id}", data, ex=60)
    
    return JSONResponse(content={"item_id": item_id, "data": data, "cached": False})

