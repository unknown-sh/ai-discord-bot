from fastapi import APIRouter, Request, HTTPException
from ai_gateway.supabase_config import get_config, set_config, get_all_config

from common.logging import log_action

from datetime import datetime

from config_engine.access import get_user_role

router = APIRouter()


@router.get("/config/{key}")
async def api_get_config(request: Request, key: str):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Missing user ID for access control"
        )

    role = await get_user_role(user_id)
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )

    value = await get_config(key)
    await log_action(
        user_id, "get_config", {"key": key, "timestamp": datetime.utcnow().isoformat()}
    )
    return {"key": key, "value": value}


@router.post("/config")
async def api_set_config(request: Request, payload: dict):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Missing user ID for access control"
        )

    role = await get_user_role(user_id)
    if role != "superadmin":
        raise HTTPException(
            status_code=403, detail="Unauthorized: superadmin role required"
        )

    key = payload.get("key")
    value = payload.get("value")
    if not key or not isinstance(key, str) or not key.strip():
        raise HTTPException(status_code=400, detail="Invalid or missing config key")
    if value is None:
        raise HTTPException(status_code=400, detail="Missing config value")

    await set_config(key, value)
    await log_action(
        user_id,
        "set_config",
        {"key": key, "value": value, "timestamp": datetime.utcnow().isoformat()},
    )
    return {"status": "ok", "key": key, "value": value}


@router.get("/config/show/{key}")
async def api_show_config(request: Request, key: str):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Missing user ID for access control"
        )

    role = await get_user_role(user_id)
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )

    value = await get_config(key)
    await log_action(
        user_id, "show_config", {"key": key, "timestamp": datetime.utcnow().isoformat()}
    )
    return {"key": key, "value": value}


@router.get("/config")
async def api_get_all_config(request: Request):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Missing user ID for access control"
        )

    role = await get_user_role(user_id)
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )

    result = await get_all_config()
    await log_action(
        user_id, "get_all_config", {"timestamp": datetime.utcnow().isoformat()}
    )
    return result
