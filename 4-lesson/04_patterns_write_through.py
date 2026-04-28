from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis.asyncio as redis
import asyncio
import time
import json

app = FastAPI()

# Simulation of the database
fake_db = {
    1: {"name": "iPhone 15", "price": 999},
    2: {"name": "MacBook Pro", "price": 2499},
    3: {"name": "AirPods Pro", "price": 249},
}

class Item(BaseModel):
    name: str
    price: float

async def get_from_database(item_id: int):
    """Simulation of a slow request to the database"""
    await asyncio.sleep(1)  # Simulation of database delay
    return fake_db.get(item_id)

async def save_to_database(item_id: int, data: dict):
    """Simulation of a slow write to the database"""
    await asyncio.sleep(1)  # Имитация задержки БД
    fake_db[item_id] = data
    return True

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.on_event("shutdown")
async def shutdown_event():
    global redis_client
    await redis_client.aclose()

@app.post("/items/{item_id}")
async def create_or_update_item(item_id: int, item: Item):
    """
    Write-Through Pattern:
    1. Save data to the database
    2. Save data to the cache
    3. Return the result
    
    Guarantees that the cache is always synchronized with the database
    """
    cache_key = f"item:{item_id}"
    
    data = item.dict()

    await save_to_database(item_id, data)

    await redis_client.set(cache_key, json.dumps(data), ex=300)  # TTL = 5 minutes
    
    return JSONResponse(content={"item_id": item_id, "data": data, "message": "Item saved to both database and cache"})

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Read with cache check:
    1. Check the cache
    2. If no data - read from the database
    3. Cache and return
    """
    start_time = time.time()
    cache_key = f"item:{item_id}"
    
    # Step 1: Check the cache
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        return JSONResponse(content={"item_id": item_id, "data": json.loads(cached_data)})
    
    data = await get_from_database(item_id)
    
    if data is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Item not found"}
        )
    
    await redis_client.set(cache_key, json.dumps(data), ex=300)
    
    return JSONResponse(content={"item_id": item_id, "data": data})

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """
    Delete with cache invalidation:
    1. Delete from the database
    2. Delete from the cache
    """
    cache_key = f"item:{item_id}"
    
    if item_id in fake_db:
        del fake_db[item_id]
    
    await redis_client.delete(cache_key)
    
    return JSONResponse(content={
        "message": f"Item {item_id} deleted from both database and cache"
    })

