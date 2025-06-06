import logging

from ai_gateway.supabase_client import supabase

FALLBACK_ROLES = {
    "402357815995400200": "superadmin",
    "393273233765433340": "user",
    "172506971373699070": "user",
    "161650201130565630": "user",
}

import asyncio


async def get_user_role(user_id: str) -> str:
    """
    Asynchronously fetch a user's role from Supabase, with fallback to predefined roles or 'guest'.
    Returns the user's role as a string.
    """
    try:
        result = await asyncio.to_thread(
            lambda: supabase.table("roles")
            .select("role")
            .eq("user_id", user_id)
            .execute()
        )
        data = result.data
        if not data:
            logging.info(f"[Supabase] No DB role found for {user_id}; returning guest")
            return "guest"
        logging.info(f"[Supabase] Role for {user_id}: {data[0]['role']}")
        return data[0]["role"]
    except Exception as e:
        fallback_role = FALLBACK_ROLES.get(user_id, "guest")
        logging.warning(
            f"[FALLBACK] Supabase role fetch failed for {user_id}: {str(e)} — using fallback role: {fallback_role}"
        )
        return fallback_role


async def set_user_role(user_id: str, username: str, role: str) -> None:
    """
    Asynchronously set a user's role in Supabase.
    Returns None.
    """
    try:
        await asyncio.to_thread(
            lambda: supabase.table("roles")
            .upsert({"user_id": user_id, "username": username, "role": role})
            .execute()
        )
        logging.info(f"[Supabase] Set role for {user_id} ({username}) to {role}")
    except Exception as e:
        logging.error(
            f"[Supabase] Failed to set role for {user_id} ({username}): {str(e)}"
        )


async def get_all_roles() -> list[dict]:
    """
    Asynchronously fetch all roles from Supabase.
    Returns a list of role dictionaries.
    """
    try:
        result = await asyncio.to_thread(
            lambda: supabase.table("roles").select("*").execute()
        )
        logging.info(f"[Supabase] Retrieved all roles")
        return result.data
    except Exception as e:
        logging.error(f"[Supabase] Failed to fetch all roles: {str(e)}")
        return []
