"""
Async memory helpers for bot/user context using the new SupabaseMemoryStore abstraction.
"""

from typing import Any, Dict, List, Optional

from mcp_server.memory_store import SupabaseMemoryStore

store = SupabaseMemoryStore()


# --- Core CRUD helpers ---
async def add_memory(user_id: str, key: str, value: Any) -> str:
    """
    Add a memory value for a user and key.
    Returns the memory key set.
    """
    return await store.set(user_id, key, value)


async def get_memory(user_id: str, key: str) -> Optional[Any]:
    """
    Retrieve a memory value for a user and key.
    Returns the value or None if not found.
    """
    return await store.get(user_id, key)


async def update_memory(user_id: str, key: str, value: Any) -> bool:
    """
    Update a memory value for a user and key.
    Returns True if successful, False otherwise.
    """
    return await store.update(user_id, key, value)


async def delete_memory(user_id: str, key: str) -> bool:
    """
    Delete a memory value for a user and key.
    Returns True if successful, False otherwise.
    """
    return await store.delete(user_id, key)


async def list_memories(user_id: str) -> List[Any]:
    """
    List all memory values for a user.
    Returns a list of values.
    """
    return await store.list(user_id)


# --- Utility wrappers for bot/global and user context ---
async def set_bot_context(key: str, value: Any) -> str:
    """
    Set a global (bot) context value for a key.
    Returns the memory key set.
    """
    return await store.set("bot", key, value)


async def get_bot_context(key: str) -> Optional[Any]:
    """
    Retrieve a global (bot) context value for a key.
    Returns the value or None if not found.
    """
    return await store.get("bot", key)


async def set_user_context(user_id: str, key: str, value: Any) -> str:
    """
    Set a user-specific context value for a key.
    Returns the memory key set.
    """
    return await store.set(user_id, key, value)


async def get_user_context(user_id: str, key: str) -> Optional[Any]:
    """
    Retrieve a user-specific context value for a key.
    Returns the value or None if not found.
    """
    return await store.get(user_id, key)
