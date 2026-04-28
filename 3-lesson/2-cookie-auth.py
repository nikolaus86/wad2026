from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from pydantic import BaseModel

app = FastAPI()

SESSIONS = set()

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginData, response: Response):
    if data.username != 'admin' or data.password != 'secret':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = "simple-session-token"
    SESSIONS.add(token)

    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        max_age=60 * 30,
        samesite="lax"
    )
    return {"message": "Logged in successfully"}

def require_auth(request: Request):
    token = request.cookies.get("session")
    if token not in SESSIONS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

@app.get("/private")
def private(_: None = Depends(require_auth)):
    return {"hello": "private"}

@app.get("/public")
def public():
    return {"hello": "public"}

@app.post("/logout")
def logout(response: Response, request: Request):
    token = request.cookies.get("session")
    if token in SESSIONS:
        SESSIONS.remove(token)
    response.delete_cookie("session")
    return {"message": "Logged out"}

