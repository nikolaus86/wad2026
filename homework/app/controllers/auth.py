from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserOut
from app.services.auth_service import AuthService
from app.services.github_oauth_service import GitHubOAuthService

router = APIRouter(tags=["auth"])


def set_auth_cookies(response: Response, tokens: dict[str, str]) -> None:
    response.set_cookie("access_token", tokens["access_token"], httponly=True, samesite="lax")
    response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True, samesite="lax", max_age=30 * 24 * 60 * 60)


@router.post("/auth/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return AuthService(db).register(payload.login, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/auth/login", response_model=TokenPair)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        user = service.authenticate(payload.login, payload.password)
        tokens = service.issue_tokens(user)
        set_auth_cookies(response, tokens)
        return tokens
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/auth/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, response: Response, db: Session = Depends(get_db)):
    try:
        tokens = AuthService(db).refresh(payload.refresh_token)
        set_auth_cookies(response, tokens)
        return tokens
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/auth/logout")
def logout(payload: RefreshRequest, response: Response, db: Session = Depends(get_db)):
    AuthService(db).logout(payload.refresh_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"ok": True}


@router.post("/auth/ui/register")
def ui_register(login: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register(login, password)
        tokens = service.issue_tokens(user)
    except ValueError:
        return RedirectResponse("/register?error=login_taken", status_code=303)
    response = RedirectResponse("/", status_code=303)
    set_auth_cookies(response, tokens)
    return response


@router.post("/auth/ui/login")
def ui_login(login: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.authenticate(login, password)
        tokens = service.issue_tokens(user)
    except ValueError:
        return RedirectResponse("/login?error=bad_credentials", status_code=303)
    response = RedirectResponse("/", status_code=303)
    set_auth_cookies(response, tokens)
    return response


@router.post("/auth/ui/logout")
def ui_logout(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        AuthService(db).logout(refresh_token)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.get("/auth/github/login")
def github_login(db: Session = Depends(get_db)):
    try:
        login_url, state = GitHubOAuthService(db).build_login_url()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    response = RedirectResponse(login_url, status_code=302)
    response.set_cookie("github_oauth_state", state, httponly=True, samesite="lax", max_age=600)
    return response


@router.get("/auth/github/callback", response_class=HTMLResponse)
async def github_callback(request: Request, code: str, state: str, db: Session = Depends(get_db)):
    expected_state = request.cookies.get("github_oauth_state")
    if not expected_state or expected_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    oauth = GitHubOAuthService(db)
    try:
        profile = await oauth.exchange_code(code)
        user = oauth.get_or_create_user(profile)
        tokens = AuthService(db).issue_tokens(user)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth failed: {exc}") from exc

    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("github_oauth_state")
    set_auth_cookies(response, tokens)
    return response
