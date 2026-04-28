from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis.asyncio as redis
import asyncio
import json
from typing import Dict
from datetime import datetime

app = FastAPI()

# Simulation of the database
fake_db = {
    1: {"name": "iPhone 15", "price": 999},
    2: {"name": "MacBook Pro", "price": 2499},
    3: {"name": "AirPods Pro", "price": 249},
}

# Queue for delayed write to the database
write_queue: Dict[int, dict] = {}

class Item(BaseModel):
    name: str
    price: float

async def get_from_database(item_id: int):
    """Simulation of a slow request to the database"""
    await asyncio.sleep(1)
    return fake_db.get(item_id)

async def save_to_database(item_id: int, data: dict):
    """Simulation of a slow write to the database"""
    await asyncio.sleep(2)  # Simulation of database delay
    fake_db[item_id] = data
    return True

async def flush_write_queue():
    """Background task for writing data from the queue to the database"""
    while True:
        await asyncio.sleep(5)  # Write to the database every 5 seconds
        
        if write_queue:
            items_to_write = list(write_queue.items())
            write_queue.clear()
            
            for item_id, data in items_to_write:
                await save_to_database(item_id, data)

async def write_to_db_delayed(item_id: int, data: dict):
    await asyncio.sleep(3)  # Delay before writing
    await save_to_database(item_id, data)

@app.on_event("startup")
async def startup_event():
    global redis_client, background_task
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    background_task = asyncio.create_task(flush_write_queue())

@app.on_event("shutdown")
async def shutdown_event():
    global redis_client, background_task
    background_task.cancel()
    
    if write_queue:
        for item_id, data in write_queue.items():
            await save_to_database(item_id, data)
    
    await redis_client.aclose()

@app.post("/items/{item_id}")
async def create_or_update_item(item_id: int, item: Item):
    """
    Write-Back (Write-Behind) Pattern:
    1. Save data ONLY to the cache (fast)
    2. Return successful response to the user
    3. Write to the database asynchronously in the background
    
    Advantages:
    - Very fast write (only cache)
    - Can batch writes to the database
    
    Disadvantages:
    - Risk of data loss in case of failure
    - Cache and database are temporarily not synchronized
    """
    cache_key = f"item:{item_id}"
    data = item.dict()
    
    await redis_client.set(cache_key, json.dumps(data), ex=600)  # TTL = 10 минут
    
    write_queue[item_id] = data
    
    return JSONResponse(content={
        "item_id": item_id,
        "data": data,
        "message": "Item saved to cache, will be written to DB shortly",
        "in_queue": len(write_queue)
    })

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Read data:
    1. First check the cache (the most recent data)
    2. If no data in the cache - read from the database
    """
    cache_key = f"item:{item_id}"
    
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        return JSONResponse(content={
            "item_id": item_id,
            "data": json.loads(cached_data),
            "source": "cache"
        })
    
    data = await get_from_database(item_id)
    
    if data is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Item not found"}
        )
    
    await redis_client.set(cache_key, json.dumps(data), ex=600)
    
    return JSONResponse(content={
        "item_id": item_id,
        "data": data,
        "source": "database"
    })

