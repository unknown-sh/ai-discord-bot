"""
Audit log endpoints for admin dashboard.
Returns audit log entries from Supabase for display in the web dashboard.
"""

from typing import Any, Dict
from ai_gateway.supabase_client import supabase
from fastapi import APIRouter, Depends, HTTPException, Request
from config_engine.access import get_user_id_and_role
import asyncio

router = APIRouter()

AUDIT_LOG_TABLE = "audit_log"


@router.get("/audit/logs")
async def get_audit_logs(
    request: Request,
    user: tuple = Depends(get_user_id_and_role),
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Retrieve audit log entries for the admin dashboard from Supabase.
    Only accessible to admin and superadmin roles.
    """
    user_id, role = user
    if role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await asyncio.to_thread(
        lambda: supabase.table(AUDIT_LOG_TABLE)
        .select("timestamp, user_id, username, action, ip, user_agent")
        .order("timestamp", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    logs = getattr(result, "data", result.get("data", []))
    return {"logs": logs}
