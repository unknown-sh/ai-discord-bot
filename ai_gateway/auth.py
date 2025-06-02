"""
Discord OAuth2 authentication endpoints for the web dashboard.
Ensures user is admin or superadmin (role from Supabase) before issuing JWT.
Supports secure cookie-based sessions, refresh tokens, logout, and CSRF protection.
"""

import os
import secrets
from datetime import datetime, timedelta

import httpx
from ai_gateway.supabase_client import supabase
from fastapi import (APIRouter, Cookie, Form, HTTPException, Request, Response,
                     status)
from fastapi.responses import JSONResponse, RedirectResponse
from jose import jwt

from config_engine.access import get_user_role

router = APIRouter()

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI", "http://localhost:3000/auth/callback"
)
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ISSUER = "ai-discord-bot"
JWT_COOKIE_NAME = "ai_dash_token"
JWT_REFRESH_COOKIE_NAME = "ai_dash_refresh"
JWT_COOKIE_MAX_AGE = 60 * 60 * 1  # 1 hour access token
JWT_REFRESH_MAX_AGE = 60 * 60 * 24 * 14  # 14 days refresh token
CSRF_COOKIE_NAME = "ai_dash_csrf"
CSRF_HEADER_NAME = "x-csrf-token"

DISCORD_AUTH_URL = (
    f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}"
    f"&redirect_uri={DISCORD_REDIRECT_URI}"
    f"&response_type=code&scope=identify"
)

# --- Auth endpoints ---

from fastapi import Query


@router.get("/api/login/discord")
async def login_discord(redirect: str = Query(None)):
    """
    Start Discord OAuth2 login. Optionally takes a ?redirect= param for post-login redirect.
    """
    # Store the redirect target in a secure cookie so it can be used after callback
    resp = RedirectResponse(DISCORD_AUTH_URL)
    if redirect:
        resp.set_cookie(
            "ai_dash_postlogin",
            redirect,
            httponly=True,
            max_age=600,
            path="/",
            samesite="lax",
        )
    return resp


from ai_gateway.audit_helpers import log_audit_event
from ai_gateway.refresh_token_store import (get_valid_refresh_token,
                                            revoke_all_tokens_for_user,
                                            rotate_refresh_token,
                                            store_refresh_token)
from ai_gateway.settings import settings

# JWT Configuration
JWT_ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iss": JWT_ISSUER})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.get("/auth/callback")
async def auth_callback(code: str, request: Request, response: Response):
    """Handle Discord OAuth2 callback, check admin role, issue JWT/refresh/csrf cookies, and store refresh token in Supabase."""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    async with httpx.AsyncClient() as client:
        # 1. Exchange code for access token
        token_resp = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_resp.status_code != 200:
            await log_audit_event(
                None, "login_failed_token_exchange", ip=ip, user_agent=user_agent
            )
            raise HTTPException(status_code=400, detail="Discord token exchange failed")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
    if not access_token:
        await log_audit_event(None, "login_failed_no_access_token", ip=ip, user_agent=user_agent)
        raise HTTPException(status_code=400, detail="No access token in Discord response")

        # 2. Fetch user info
        user_resp = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_resp.status_code != 200:
            await log_audit_event(
                None, "login_failed_userinfo", ip=ip, user_agent=user_agent
            )
            raise HTTPException(
                status_code=400, detail="Could not fetch Discord user info"
            )

        user = user_resp.json()
        discord_id = user.get("id")
        username = user.get("username")
    if not discord_id or not username:
        await log_audit_event(None, "login_failed_missing_user_info", ip=ip, user_agent=user_agent)
        raise HTTPException(status_code=400, detail="Discord user info missing id or username")

    # 3. Check role in Supabase
    role = await get_user_role(discord_id)
    if not role:
        await log_audit_event(discord_id, "login_failed_no_role", username=username, ip=ip, user_agent=user_agent)
        raise HTTPException(status_code=403, detail="No role assigned to user")
    if role not in ("admin", "superadmin"):
        await log_audit_event(
            discord_id,
            "login_denied_role",
            username=username,
            ip=ip,
            user_agent=user_agent,
        )
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # 4. Generate JWT tokens
    access_token = create_access_token(
        {"sub": discord_id, "username": username, "role": role, "avatar": user.get("avatar", "")}
    )
    refresh_token = secrets.token_urlsafe(64)
    csrf_token = secrets.token_urlsafe(32)

    # 5. Store refresh token in Supabase
    await store_refresh_token(discord_id, refresh_token)

    # 6. Set secure, HTTP-only cookies
    response = RedirectResponse("/dashboard")
    # For local dev, set domain=None and secure=False to ensure cookies are accepted on localhost
    cookie_params = {
        "httponly": True,
        "secure": False,  # Must be False for localhost unless using HTTPS
        "samesite": "lax",
        "domain": None,   # Explicitly None for localhost
        "path": "/"
    }
    response.set_cookie(
        key="ai_dash_token",
        value=f"Bearer {access_token}",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **cookie_params
    )
    response.set_cookie(
        key="ai_dash_refresh",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **cookie_params
    )
    response.set_cookie(
        key="ai_dash_csrf",
        value=csrf_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=False,  # CSRF token should be readable by JS
        secure=False,
        samesite="lax",
        domain=None,
        path="/"
    )

    # 7. Log successful login
    await log_audit_event(
        discord_id, "login_success", username=username, ip=ip, user_agent=user_agent
    )

    # 8. Handle post-login redirect if any
    postlogin = request.cookies.get("ai_dash_postlogin")
    if postlogin:
        response = RedirectResponse(url=postlogin, status_code=303)
        response.delete_cookie("ai_dash_postlogin", path="/")

    return response


@router.post("/auth/refresh")
async def auth_refresh(
    request: Request,
    response: Response,
    ai_dash_refresh: str = Cookie(None),
    ai_dash_csrf: str = Cookie(None),
    x_csrf_token: str = Form(None),
):
    """Refresh access token using refresh token and CSRF token; rotate refresh token in Supabase."""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    try:
        if not ai_dash_refresh or not ai_dash_csrf or not x_csrf_token:
            raise HTTPException(status_code=401, detail="Missing refresh or CSRF token")
        if ai_dash_csrf != x_csrf_token:
            raise HTTPException(status_code=403, detail="CSRF token mismatch")
        payload = jwt.decode(
            ai_dash_refresh, JWT_SECRET, algorithms=["HS256"], issuer=JWT_ISSUER
        )
        if payload.get("type") != "refresh":
            raise Exception()
        user_id = payload["sub"]
        # Validate and get refresh token row
        row = await get_valid_refresh_token(user_id, ai_dash_refresh, ip, user_agent)
        if not row:
            await log_audit_event(
                user_id, "refresh_denied", ip=ip, user_agent=user_agent
            )
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token (db)"
            )
        # Rotate refresh token
        now = datetime.utcnow()
        exp = now + timedelta(seconds=JWT_COOKIE_MAX_AGE)
        refresh_exp = now + timedelta(seconds=JWT_REFRESH_MAX_AGE)
        jwt_payload = {
            "sub": user_id,
            "username": payload.get("username", ""),
            "role": payload.get("role", "admin"),
            "iss": JWT_ISSUER,
            "exp": exp,
            "type": "access",
        }
        new_refresh_payload = {
            "sub": user_id,
            "iss": JWT_ISSUER,
            "exp": refresh_exp,
            "type": "refresh",
        }
        token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")
        new_refresh_token = jwt.encode(
            new_refresh_payload, JWT_SECRET, algorithm="HS256"
        )
        await rotate_refresh_token(
            row["id"], user_id, new_refresh_token, refresh_exp, ip, user_agent
        )
        await log_audit_event(user_id, "refresh_success", ip=ip, user_agent=user_agent)
        resp = JSONResponse({"status": "ok"})
        resp.set_cookie(
            key=JWT_COOKIE_NAME,
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=JWT_COOKIE_MAX_AGE,
            path="/",
        )
        resp.set_cookie(
            key=JWT_REFRESH_COOKIE_NAME,
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=JWT_REFRESH_MAX_AGE,
            path="/",
        )
        return resp
    except Exception as e:
        await log_audit_event(None, "refresh_error", ip=ip, user_agent=user_agent)
        raise


@router.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    """Logout by clearing the auth and refresh cookies and revoking all tokens for the user."""
    user_id = None
    # Try to extract user from access or refresh token
    token = request.cookies.get(JWT_COOKIE_NAME) or request.cookies.get(
        JWT_REFRESH_COOKIE_NAME
    )
    if token:
        try:
            payload = jwt.decode(
                token, JWT_SECRET, algorithms=["HS256"], issuer=JWT_ISSUER
            )
            user_id = payload.get("sub")
        except Exception:
            pass
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    if user_id:
        await revoke_all_tokens_for_user(user_id)
        await log_audit_event(user_id, "logout", ip=ip, user_agent=user_agent)
    else:
        await log_audit_event(None, "logout_no_user", ip=ip, user_agent=user_agent)
    resp = Response(content="Logged out", status_code=200)
    resp.delete_cookie(JWT_COOKIE_NAME, path="/")
    resp.delete_cookie(JWT_REFRESH_COOKIE_NAME, path="/")
    resp.delete_cookie(CSRF_COOKIE_NAME, path="/")
    return resp


@router.get("/auth/me")
async def auth_me(request: Request):
    """Return info about the current user from JWT (from cookie or header), for dashboard frontend."""
    token = None
    # Prefer cookie
    if JWT_COOKIE_NAME in request.cookies:
        token = request.cookies[JWT_COOKIE_NAME]
    # Fallback to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    if not token:
        return {"id": None, "username": None, "avatar": None, "role": None}
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], issuer=JWT_ISSUER)
    except Exception:
        return {"id": None, "username": None, "avatar": None, "role": None}
    return {
        "id": payload["sub"],
        "username": payload.get("username", ""),
        "avatar": payload.get("avatar", ""),
        "role": payload.get("role", ""),
    }
