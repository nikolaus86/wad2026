from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
import uvicorn
import requests

GOOGLE_CLIENT_ID = "aaa"
GOOGLE_CLIENT_SECRET = "bbb"
GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google/callback"

app = FastAPI()
router = APIRouter()

@router.get("/auth-google")
async def auth_google():
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope=openid email profile")

@router.get("/auth/google/callback")
async def callback(code: str):
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    )

    if token_resp.status_code != 200:
        return {"error": "Failed to get token", "details": token_resp.text}

    tokens = token_resp.json()

    access_token = tokens.get("access_token")
    user_info = None
    if access_token:
        user_info_resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_info_resp.status_code == 200:
            user_info = user_info_resp.json()

    return {
        "user_info": user_info
    }


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)