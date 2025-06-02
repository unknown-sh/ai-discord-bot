# In-memory memory store fallback for MCP server
from typing import Any, List, Optional


class SupabaseMemoryStore:
    """
    Async in-memory fallback implementation for bot/user context memory storage.

    Methods:
        get(user_id, key): Retrieve a value by user and key.
        set(user_id, key, value): Set a value for user and key.
        update(user_id, key, value): Update a value for user and key if it exists.
        delete(user_id, key): Delete a value for user and key.
        list(user_id): List all values for a user.
    """
    def __init__(self) -> None:
        self.memory: dict[str, dict[str, Any]] = {}

    async def get(self, user_id: str, key: str) -> Optional[Any]:
        """
        Retrieve a value for a user and key.
        Returns the value or None if not found.
        """
        return self.memory.get(user_id, {}).get(key)

    async def set(self, user_id: str, key: str, value: Any) -> str:
        """
        Set a value for a user and key.
        Returns the key set.
        """
        if user_id not in self.memory:
            self.memory[user_id] = {}
        self.memory[user_id][key] = value
        return key

    async def update(self, user_id: str, key: str, value: Any) -> bool:
        """
        Update a value for a user and key if it exists.
        Returns True if updated, False otherwise.
        """
        if user_id in self.memory and key in self.memory[user_id]:
            self.memory[user_id][key] = value
            return True
        return False

    async def delete(self, user_id: str, key: str) -> bool:
        """
        Delete a value for a user and key.
        Returns True if deleted, False otherwise.
        """
        if user_id in self.memory and key in self.memory[user_id]:
            del self.memory[user_id][key]
            return True
        return False

    async def list(self, user_id: str) -> List[Any]:
        """
        List all values for a user.
        Returns a list of values.
        """
        return list(self.memory.get(user_id, {}).values())
