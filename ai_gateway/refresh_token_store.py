"""
Async Supabase refresh token store for secure session rotation and revocation.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional

from ai_gateway.supabase_client import supabase

REFRESH_TOKEN_TABLE = "refresh_tokens"


async def hash_token(token: str) -> str:
    """
    Hash a refresh token using SHA-256 for secure storage.
    """
    return hashlib.sha256(token.encode()).hexdigest()


async def store_refresh_token(
    user_id: str,
    token: str,
    expires_at: datetime,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Store a new refresh token in Supabase for the given user.
    """
    token_hash = await hash_token(token)
    await asyncio.to_thread(
        lambda: supabase.table(REFRESH_TOKEN_TABLE)
        .insert(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "issued_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat(),
                "ip": ip,
                "user_agent": user_agent,
                "revoked": False,
            }
        )
        .execute()
    )


async def get_valid_refresh_token(
    user_id: str, token: str, ip: Optional[str] = None, user_agent: Optional[str] = None
) -> Optional[dict]:
    """
    Retrieve a valid, non-revoked refresh token for a user from Supabase.
    Checks expiry and optional IP/user-agent match.
    """
    token_hash = await hash_token(token)
    query = (
        supabase.table(REFRESH_TOKEN_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .eq("token_hash", token_hash)
        .eq("revoked", False)
    )
    if ip:
        query = query.eq("ip", ip)
    if user_agent:
        query = query.eq("user_agent", user_agent)
    data = (await query.execute()).data
    if not data:
        return None
    row = data[0]
    if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
        return None
    return row


async def revoke_refresh_token(token_id: str) -> None:
    """
    Revoke a specific refresh token by its ID in Supabase.
    """
    await asyncio.to_thread(
        lambda: supabase.table(REFRESH_TOKEN_TABLE)
        .update({"revoked": True})
        .eq("id", token_id)
        .execute()
    )


async def revoke_all_tokens_for_user(user_id: str) -> None:
    """
    Revoke all refresh tokens for a given user in Supabase.
    """
    await asyncio.to_thread(
        lambda: supabase.table(REFRESH_TOKEN_TABLE)
        .update({"revoked": True})
        .eq("user_id", user_id)
        .execute()
    )


async def rotate_refresh_token(
    old_token_id: str,
    user_id: str,
    new_token: str,
    expires_at: datetime,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Rotate a refresh token: revoke the old one and store the new one atomically.
    """
    await revoke_refresh_token(old_token_id)
    await store_refresh_token(user_id, new_token, expires_at, ip, user_agent)
