"""
Helpers for bot/global and user context memory access via MCP server endpoints.
"""

import os
from typing import Any, Dict
import httpx

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://mcp_server:8000")


async def get_bot_context(key: str) -> Dict[str, Any]:
    """
    Retrieve context for the bot (global context) from the MCP server.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{MCP_SERVER_URL}/memory/{key}", headers={"X-User-ID": "bot"}
        )
        resp.raise_for_status()
        return resp.json()


async def set_bot_context(key: str, value: str) -> Dict[str, Any]:
    """
    Set context for the bot (global context) on the MCP server.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MCP_SERVER_URL}/memory",
            json={"key": key, "value": value},
            headers={"X-User-ID": "bot"},
        )
        resp.raise_for_status()
        return resp.json()


async def get_user_context(user_id: str, key: str) -> Dict[str, Any]:
    """
    Retrieve context for a specific user from the MCP server.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{MCP_SERVER_URL}/memory/{key}", headers={"X-User-ID": user_id}
        )
        resp.raise_for_status()
        return resp.json()


async def set_user_context(user_id: str, key: str, value: str) -> Dict[str, Any]:
    """
    Set context for a specific user on the MCP server.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MCP_SERVER_URL}/memory",
            json={"key": key, "value": value},
            headers={"X-User-ID": user_id},
        )
        resp.raise_for_status()
        return resp.json()
