"""
In-memory implementation of BaseMemoryStore for testing and local development.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, List, Optional

from .base import BaseMemoryStore


class InMemoryMemoryStore(BaseMemoryStore):
    def __init__(self):
        self._store = {}
        self._lock = asyncio.Lock()

    async def set(self, user_id: str, key: str, value: Any) -> str:
        async with self._lock:
            now = datetime.utcnow().isoformat()
            if user_id not in self._store:
                self._store[user_id] = {}
            self._store[user_id][key] = {
                "value": json.dumps(value),
                "updated_at": now,
                "created_at": now,
            }
            return f"{user_id}:{key}"

    async def get(self, user_id: str, key: str) -> Optional[Any]:
        async with self._lock:
            try:
                entry = self._store[user_id][key]
                return json.loads(entry["value"])
            except Exception:
                return None

    async def update(self, user_id: str, key: str, value: Any) -> bool:
        async with self._lock:
            if user_id in self._store and key in self._store[user_id]:
                now = datetime.utcnow().isoformat()
                self._store[user_id][key]["value"] = json.dumps(value)
                self._store[user_id][key]["updated_at"] = now
                return True
            return False

    async def delete(self, user_id: str, key: str) -> bool:
        async with self._lock:
            if user_id in self._store and key in self._store[user_id]:
                del self._store[user_id][key]
                return True
            return False

    async def list(self, user_id: str) -> List[Any]:
        async with self._lock:
            if user_id not in self._store:
                return []
            result = []
            for key, entry in self._store[user_id].items():
                try:
                    value = json.loads(entry["value"])
                except Exception:
                    value = entry["value"]
                result.append(
                    {"key": key, "value": value, "updated_at": entry["updated_at"]}
                )
            return result
