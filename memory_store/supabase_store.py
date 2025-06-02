"""
Async Supabase-backed implementation of BaseMemoryStore.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, List, Optional

from ai_gateway.supabase_client import supabase

from .base import BaseMemoryStore


class SupabaseMemoryStore(BaseMemoryStore):
    async def set(self, user_id: str, key: str, value: Any) -> str:
        now = datetime.utcnow().isoformat()
        data = {
            "user_id": user_id,
            "key": key,
            "value": json.dumps(value),
            "created_at": now,
            "updated_at": now,
        }
        res = await asyncio.to_thread(
            lambda: supabase.table("memory").insert(data).execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]["id"]
        raise Exception(f"Failed to set memory for user {user_id} and key {key}")

    async def get(self, user_id: str, key: str) -> Optional[Any]:
        res = await asyncio.to_thread(
            lambda: supabase.table("memory")
            .select("*")
            .eq("user_id", user_id)
            .eq("key", key)
            .limit(1)
            .execute()
        )
        data = res.data
        if data:
            try:
                return json.loads(data[0]["value"])
            except Exception:
                return data[0]["value"]
        return None

    async def update(self, user_id: str, key: str, value: Any) -> bool:
        now = datetime.utcnow().isoformat()
        res = await asyncio.to_thread(
            lambda: supabase.table("memory")
            .update({"value": json.dumps(value), "updated_at": now})
            .eq("user_id", user_id)
            .eq("key", key)
            .execute()
        )
        return bool(res.data)

    async def delete(self, user_id: str, key: str) -> bool:
        res = await asyncio.to_thread(
            lambda: supabase.table("memory")
            .delete()
            .eq("user_id", user_id)
            .eq("key", key)
            .execute()
        )
        return bool(res.data)

    async def list(self, user_id: str) -> List[Any]:
        res = await asyncio.to_thread(
            lambda: supabase.table("memory")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        result = []
        for item in res.data or []:
            try:
                value = json.loads(item["value"])
            except Exception:
                value = item["value"]
            result.append(
                {"key": item["key"], "value": value, "updated_at": item["updated_at"]}
            )
        return result
