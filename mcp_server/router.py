from datetime import datetime
from typing import Any, Dict, Tuple

from ai_gateway.supabase_config import get_all_config, get_config, set_config
from fastapi import APIRouter, Depends, HTTPException, Request

from common.custom_logging import log_action
from config_engine.access import get_user_role

router = APIRouter()

from . import memory

from fastapi import Depends

async def get_user_id_and_role(request: Request) -> Tuple[str, str]:
    """
    Dependency to extract user_id and role from request headers.
    Raises HTTPException if missing or not authorized.
    Returns a tuple of (user_id, role).
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Missing user ID for access control"
        )
    role = await get_user_role(user_id)
    return user_id, role

@router.get("/mcp/get_all_roles")
async def api_get_all_roles(user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)):
    """
    List all roles and their users. Admin/superadmin only.
    """
    user_id, role = user_and_role
    if role not in ("superadmin", "admin"):
        raise HTTPException(status_code=403, detail="Unauthorized: admin or superadmin role required")
    from ai_gateway.supabase_roles import get_all_roles
    result = await get_all_roles()
    await log_action(user_id, "get_all_roles", {"timestamp": datetime.utcnow().isoformat()})
    return result


@router.get("/healthz")
async def healthz() -> Dict[str, str]:
    """
    Healthcheck endpoint for infra/monitoring.
    Returns status OK.
    """
    return {"status": "ok"}


@router.get("/mcp/actions")
async def mcp_list_actions():
    """
    List all available MCP actions and their schemas for discovery by clients.
    """
    return [
        {"name": "get_all_roles", "description": "List all roles and their users", "parameters": {}, "permissions": ["admin", "superadmin"]},
        {"name": "get_user_role", "description": "Get the role for a specific user", "parameters": {"user_id": "string"}, "permissions": ["admin", "superadmin"]},
        {"name": "set_user_role", "description": "Set a user's role", "parameters": {"user_id": "string", "role": "string"}, "permissions": ["superadmin"]},
        {"name": "get_config", "description": "Show all config values", "parameters": {}, "permissions": ["admin", "superadmin"]},
        {"name": "get_config_key", "description": "Show value for a config key", "parameters": {"key": "string"}, "permissions": ["admin", "superadmin"]},
        {"name": "set_config", "description": "Set a config value", "parameters": {"key": "string", "value": "string"}, "permissions": ["admin", "superadmin"]},
        {"name": "delete_config", "description": "Delete a config key", "parameters": {"key": "string"}, "permissions": ["superadmin"]},
        {"name": "list_config_keys", "description": "List all config keys", "parameters": {}, "permissions": ["admin", "superadmin"]},
        {"name": "config_help", "description": "Show config help or help for a specific key", "parameters": {"key": "string (optional)"}, "permissions": ["admin", "superadmin"]},
        {"name": "get_audit_log", "description": "Show audit log entries", "parameters": {"limit": "int (default 10)"}, "permissions": ["superadmin"]},
        {"name": "help", "description": "Show help for a command", "parameters": {"command": "string (optional)"}, "permissions": ["all"]},
    ]


@router.post("/memory")
async def api_add_memory(
    payload: Dict[str, str],
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
) -> Dict[str, str]:
    """
    Add a memory for the authenticated user. Payload: {key, value}
    Returns the key set.
    """
    user_id, _ = user_and_role
    key = payload.get("key")
    value = payload.get("value")
    if not key or value is None:
        raise HTTPException(status_code=400, detail="Missing key or value in payload")
    memory_id = await memory.add_memory(user_id, key, value)
    await log_action(user_id, "add_memory", f"key={key}")
    return {"result": memory_id}


# --- Admin endpoints for bot/global context ---


@router.get("/bot-context/{key}")
async def api_get_bot_context(
    key: str, user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, str]:
    """
    Get a global/bot context value by key. Admin/superadmin only.
    Returns the value for the specified key.
    """
    _, role = user_and_role
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )
    mem = await memory.get_memory("bot", key)
    if not mem:
        raise HTTPException(status_code=404, detail="Bot context not found")
    return mem


@router.post("/bot-context")
async def api_set_bot_context(
    payload: Dict[str, str],
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
) -> Dict[str, str]:
    """
    Set a global/bot context value. Payload: {key, value}. Admin/superadmin only.
    Returns the key set.
    """
    _, role = user_and_role
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )
    key = payload.get("key")
    value = payload.get("value")
    if not key or value is None:
        raise HTTPException(status_code=400, detail="Missing key or value")
    mem_id = await memory.add_memory("bot", key, value)
    return {"status": "ok", "id": mem_id}


@router.get("/memory/{key}")
async def api_get_memory(
    key: str, user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, Any]:
    """
    Get a memory for the authenticated user by key.
    Returns the value for the specified key.
    """
    user_id, _ = user_and_role
    mem = await memory.get_memory(user_id, key)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    return mem


@router.put("/memory/{key}")
async def api_update_memory(
    key: str,
    payload: Dict[str, str],
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
) -> Dict[str, str]:
    """
    Update a memory for the authenticated user by key. Payload: {value}
    Returns status OK if successful.
    """
    user_id, _ = user_and_role
    value = payload.get("value")
    if value is None:
        raise HTTPException(status_code=400, detail="Missing value")
    updated = await memory.update_memory(user_id, key, value)
    if not updated:
        raise HTTPException(status_code=404, detail="Memory not found or not updated")
    return {"status": "ok"}


@router.delete("/memory/{key}")
async def api_delete_memory(
    key: str, user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, str]:
    """
    Delete a memory for the authenticated user by key.
    Returns status OK if successful.
    """
    user_id, _ = user_and_role
    deleted = await memory.delete_memory(user_id, key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found or not deleted")
    return {"status": "ok"}


@router.get("/memories")
async def api_list_memories(
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
) -> Any:
    """
    List all memories for the authenticated user.
    Returns a list of all memory values for the user.
    """
    user_id, _ = user_and_role
    mems = await memory.list_memories(user_id)
    return mems


@router.get("/config/{key}")
async def api_get_config(
    key: str, user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, Any]:
    """
    Get a config value by key.

    Args:
    - key (str): The config key to retrieve.

    Returns:
    - Dict[str, Any]: A dictionary containing the config key and value.

    Raises:
    - HTTPException: If the user is not authorized (admin or superadmin role required).
    """
    user_id, role = user_and_role
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
async def api_set_config(
    payload: Dict[str, Any],
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
) -> Dict[str, Any]:
    """
    Set a config value.

    Args:
    - payload (Dict[str, Any]): A dictionary containing the config key and value.

    Returns:
    - Dict[str, Any]: A dictionary containing the config key and new value.

    Raises:
    - HTTPException: If the user is not authorized (superadmin role required).
    """
    user_id, role = user_and_role
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
async def api_show_config(
    key: str, user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, Any]:
    """
    Show a config value.

    Args:
    - key (str): The config key to retrieve.

    Returns:
    - Dict[str, Any]: A dictionary containing the config key and value.

    Raises:
    - HTTPException: If the user is not authorized (admin or superadmin role required).
    """
    user_id, role = user_and_role
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
async def api_get_all_config(
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
) -> Any:
    """
    Get all config values.

    Returns:
    - Any: A dictionary or list containing all config values.

    Raises:
    - HTTPException: If the user is not authorized (admin or superadmin role required).
    """
    user_id, role = user_and_role
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )
    result = await get_all_config()
    await log_action(
        user_id, "get_all_config", {"timestamp": datetime.utcnow().isoformat()}
    )
    return result


@router.delete("/config/delete/{key}")
async def api_delete_config(
    key: str, user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, str]:
    """
    Delete a config key. Superadmin only.
    """
    user_id, role = user_and_role
    if role != "superadmin":
        raise HTTPException(status_code=403, detail="Unauthorized: superadmin role required")
    from ai_gateway.supabase_client import supabase
    await supabase.table("bot_config").delete().eq("key", key).execute()
    await log_action(user_id, "delete_config", {"key": key, "timestamp": datetime.utcnow().isoformat()})
    return {"status": "ok", "deleted_key": key}


@router.get("/config/keys")
async def api_list_config_keys(
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role)
) -> Dict[str, Any]:
    """
    List all config keys. Admin/superadmin only.
    """
    user_id, role = user_and_role
    if role not in ("superadmin", "admin"):
        raise HTTPException(
            status_code=403, detail="Unauthorized: admin or superadmin role required"
        )
    from ai_gateway.supabase_client import supabase
    res = await supabase.table("bot_config").select("key").execute()
    keys = [row["key"] for row in res.data] if res.data else []
    await log_action(user_id, "list_config_keys", {"timestamp": datetime.utcnow().isoformat()})
    return {"keys": keys}


@router.get("/audit/logs")
async def api_get_audit_logs(
    user_and_role: Tuple[str, str] = Depends(get_user_id_and_role),
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get audit log entries. Superadmin only.
    """
    user_id, role = user_and_role
    if role != "superadmin":
        raise HTTPException(status_code=403, detail="Unauthorized: superadmin role required")
    from ai_gateway.supabase_client import supabase
    result = supabase.table("audit_log").select("timestamp, user_id, username, action, ip, user_agent").order("timestamp", desc=True).limit(limit).execute()
    logs = result.data if hasattr(result, "data") else []
    await log_action(user_id, "get_audit_log", {"limit": limit, "timestamp": datetime.utcnow().isoformat()})
    return {"logs": logs}
