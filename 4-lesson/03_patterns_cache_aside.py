from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import asyncio
import time

app = FastAPI()

# Database simulation
fake_db = {
    1: {"name": "iPhone 15", "price": 999},
    2: {"name": "MacBook Pro", "price": 2499},
    3: {"name": "AirPods Pro", "price": 249},
}

async def get_from_database(item_id: int):
    """Simulation of a slow database request"""
    await asyncio.sleep(2)  # Simulation of database delay
    return fake_db.get(item_id)

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
    """
    Cache-Aside (Lazy Loading) Pattern:
    1. Check the cache
    2. If no data - read from the database
    3. Save to the cache
    4. Return the data
    """
    cache_key = f"item:{item_id}"
    
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        return JSONResponse(content={
            "item_id": item_id,
            "data": cached_data,
        })
    
    data = await get_from_database(item_id)
    
    if data is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Item not found"}
        )
    
    await redis_client.set(cache_key, json.dumps(data), ex=60)
    
    return JSONResponse(content={"item_id": item_id, "data": data})



