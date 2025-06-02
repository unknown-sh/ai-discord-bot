"""
FastAPI endpoints for persistent user and bot context using MCP server memory API.
"""

from typing import Any, Dict

from ai_gateway.bot_context import (get_bot_context, get_user_context,
                                    set_bot_context, set_user_context)
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()


async def get_authenticated_user(request: Request) -> str:
    """
    Extract and validate the authenticated user ID from the request headers.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID")
    return user_id


@router.get("/user-context/{key}")
async def api_get_user_context(
    key: str, user_id: str = Depends(get_authenticated_user)
) -> Dict[str, Any]:
    """
    Retrieve persistent context value for the authenticated user.
    """
    context = await get_user_context(user_id, key)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context


@router.post("/user-context/{key}")
async def api_set_user_context(
    key: str, payload: Dict[str, Any], user_id: str = Depends(get_authenticated_user)
) -> Dict[str, str]:
    """
    Set persistent context value for the authenticated user.
    """
    value = payload.get("value")
    if value is None:
        raise HTTPException(status_code=400, detail="Missing value")
    await set_user_context(user_id, key, value)
    return {"status": "ok"}


@router.get("/bot-context/{key}")
async def api_get_bot_context(key: str, request: Request) -> Dict[str, Any]:
    """
    Retrieve global/bot context value (admin/superadmin only).
    """
    user_id = request.headers.get("X-User-ID")
    role = request.headers.get("X-User-Role", "guest")
    if role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    context = await get_bot_context(key)
    if not context:
        raise HTTPException(status_code=404, detail="Bot context not found")
    return context


@router.post("/bot-context/{key}")
async def api_set_bot_context(
    key: str, payload: Dict[str, Any], request: Request
) -> Dict[str, str]:
    """
    Set global/bot context value (admin/superadmin only).
    """
    user_id = request.headers.get("X-User-ID")
    role = request.headers.get("X-User-Role", "guest")
    if role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    value = payload.get("value")
    if value is None:
        raise HTTPException(status_code=400, detail="Missing value")
    await set_bot_context(key, value)
    return {"status": "ok"}
