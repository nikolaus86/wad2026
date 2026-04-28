from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()

API_KEY = "mysecretapikey"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
    )

@app.get("/private")
async def secure_data(api_key: str = Depends(get_api_key)):
    return {"message": "Private endpoint, auth needed"}

@app.get("/public")
async def public():
    return {"message": "Public endpoint, no auth needed"}