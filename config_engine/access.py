import asyncio
from typing import Tuple

from ai_gateway.supabase_roles import get_user_role
from fastapi import HTTPException, Request

# Re-export get_user_role for compatibility

__all__ = ["get_user_role", "get_user_id_and_role"]


async def get_user_id_and_role(request: Request) -> Tuple[str, str]:
    """
    Dependency to extract user_id and role from request headers.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        Tuple[str, str]: A tuple containing the user_id and role.

    Raises:
        HTTPException: If the user_id is missing from the headers.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=400, detail="Missing user ID for access control"
        )
    # Use the imported get_user_role
    role = await get_user_role(user_id)
    return user_id, role
