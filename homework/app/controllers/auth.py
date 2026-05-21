from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserOut
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


def set_auth_cookies(response: Response, tokens: dict[str, str]) -> None:
    response.set_cookie("access_token", tokens["access_token"], httponly=True, samesite="lax")
    response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True, samesite="lax", max_age=30 * 24 * 60 * 60)


@router.post("/auth/register", response_model=UserOut)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await AuthService(db).register(payload.login, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/auth/login", response_model=TokenPair)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await AuthService(db).login(payload.login, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    set_auth_cookies(response, tokens)
    return tokens


@router.post("/auth/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await AuthService(db).refresh(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    set_auth_cookies(response, tokens)
    return tokens


@router.post("/auth/logout")
async def logout(payload: RefreshRequest, response: Response, db: AsyncSession = Depends(get_db)):
    await AuthService(db).logout(payload.refresh_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"ok": True}


@router.post("/auth/ui/register")
async def ui_register(login: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        tokens = await AuthService(db).register_and_issue_tokens(login, password)
    except ValueError:
        return RedirectResponse("/register?error=login_taken", status_code=303)

    response = RedirectResponse("/", status_code=303)
    set_auth_cookies(response, tokens)
    return response


@router.post("/auth/ui/login")
async def ui_login(login: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        tokens = await AuthService(db).login(login, password)
    except ValueError:
        return RedirectResponse("/login?error=bad_credentials", status_code=303)

    response = RedirectResponse("/", status_code=303)
    set_auth_cookies(response, tokens)
    return response


@router.post("/auth/ui/logout")
async def ui_logout(request: Request, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await AuthService(db).logout(refresh_token)

    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.get("/auth/github/login")
async def github_login(db: AsyncSession = Depends(get_db)):
    try:
        login_url, state = AuthService(db).build_github_login_url()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response = RedirectResponse(login_url, status_code=302)
    response.set_cookie("github_oauth_state", state, httponly=True, samesite="lax", max_age=600)
    return response


@router.get("/auth/github/callback", response_class=HTMLResponse)
async def github_callback(request: Request, code: str, state: str, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await AuthService(db).login_with_github(code, state, request.cookies.get("github_oauth_state"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth failed: {exc}") from exc

    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("github_oauth_state")
    set_auth_cookies(response, tokens)
    return response
