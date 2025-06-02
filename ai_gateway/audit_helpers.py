"""
Helper for writing audit log events to Supabase audit_log table.
"""

from datetime import datetime
from typing import Optional
import asyncio

from ai_gateway.supabase_client import supabase

AUDIT_LOG_TABLE = "audit_log"


async def log_audit_event(
    user_id: str,
    action: str,
    username: Optional[str] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Asynchronously write an audit event to the Supabase audit_log table.
    """
    await asyncio.to_thread(
        lambda: supabase.table(AUDIT_LOG_TABLE)
        .insert(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "username": username,
                "action": action,
                "ip": ip,
                "user_agent": user_agent,
            }
        )
        .execute()
    )
