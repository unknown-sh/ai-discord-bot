from ai_gateway.audit_helpers import log_audit_event
from ai_gateway.decorators import with_permission
from ai_gateway.supabase_config import get_all_config, get_config, set_config
from fastapi import APIRouter, Request
from pydantic import BaseModel

from config_engine.help_text import CONFIG_HELP

router = APIRouter()


class ConfigUpdate(BaseModel):
    value: str


@router.get("/show/config")
@with_permission(["admin", "superadmin"])
async def show_config_list(
    request: Request, user_id=None, user_id_ctx=None, username=None, role=None
) -> dict:
    user_id = user_id or user_id_ctx
    await log_audit_event(
        user_id,
        "list_config_keys",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    lines = [f"{k}: {v['desc']}" for k, v in CONFIG_HELP.items()]
    return {"text": "Available config keys:\n" + "\n".join(lines)}


@router.get("/show/config/{key}")
@with_permission(["admin", "superadmin"])
async def show_config_key(
    key: str, request: Request, user_id=None, user_id_ctx=None, username=None, role=None
) -> dict:
    user_id = user_id or user_id_ctx
    await log_audit_event(
        user_id,
        f"show_config_key:{key}",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    value = await get_config(key)
    if value is None:
        return {"text": f"No value set for config key: {key}"}
    return {"text": f"Current value for `{key}`: {value}"}


@router.post("/set/config/{key}")
@with_permission(["admin", "superadmin"])
async def set_config_key(
    key: str,
    payload: ConfigUpdate,
    request: Request,
    user_id=None,
    username=None,
    role=None,
):
    await log_audit_event(
        user_id,
        f"set_config_key:{key}",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await set_config(key, payload.value)
    return {"status": "ok"}


@router.delete("/delete/config/{key}")
@with_permission(["admin", "superadmin"])
async def delete_config_key(
    key: str, request: Request, user_id=None, username=None, role=None
):
    await log_audit_event(
        user_id,
        f"delete_config_key:{key}",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    # Implement deletion logic here (if supported)
    return {"status": "deleted (not implemented)"}


@router.get("/config/status")
@with_permission(["admin", "superadmin"])
async def config_status(request: Request, user_id=None, user_id_ctx=None, username=None, role=None):
    """
    Returns a summary of the current config: provider, model, and personality.
    """
    user_id = user_id or user_id_ctx
    await log_audit_event(
        user_id,
        "config_status",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    provider = await get_config("AI_PROVIDER")
    model = await get_config("OPENAI_MODEL")
    personality = await get_config("AI_PERSONALITY")
    return {
        "provider": provider,
        "model": model,
        "personality": personality,
    }


@router.get("/config/debug-supabase")
async def debug_supabase():
    print("[DEBUG] /config/debug-supabase handler invoked")
    import os
    import traceback
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    debug = {}
    # Try get_all_config
    try:
        debug['all_config'] = await get_all_config()
    except Exception as e:
        debug['all_config'] = {"error": str(e), "traceback": traceback.format_exc()}
    # Try get_config for provider
    try:
        debug['provider'] = await get_config("AI_PROVIDER")
    except Exception as e:
        debug['provider'] = {"error": str(e), "traceback": traceback.format_exc()}
    # Try get_config for model
    try:
        debug['model'] = await get_config("OPENAI_MODEL")
    except Exception as e:
        debug['model'] = {"error": str(e), "traceback": traceback.format_exc()}
    # Try get_config for personality
    try:
        debug['personality'] = await get_config("AI_PERSONALITY")
    except Exception as e:
        debug['personality'] = {"error": str(e), "traceback": traceback.format_exc()}
    debug['supabase_url'] = supabase_url
    debug['supabase_key_present'] = bool(supabase_key and len(supabase_key) > 10)
    return debug

