from functools import wraps
from typing import Any, Callable, Awaitable, Tuple, List
from ai_gateway.supabase_roles import get_user_role
from fastapi import HTTPException, Request, status
from common.custom_logging import logger


def extract_discord_headers(request: Request) -> Tuple[str, str]:
    """
    Extract Discord user ID and username from request headers.
    """
    user_id = request.headers.get("x-discord-user-id", "unknown")
    username = request.headers.get("x-discord-username", "unknown")
    return user_id, username


def with_discord_headers(endpoint: Callable) -> Callable:
    """
    Decorator to inject Discord user_id and username from headers into endpoint kwargs.
    """
    @wraps(endpoint)
    def wrapper(*args, **kwargs):
        request = kwargs.get("request") or (args[0] if args else None)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Request object missing"
            )
        user_id, username = extract_discord_headers(request)
        kwargs["user_id"] = user_id
        kwargs["username"] = username
        return endpoint(*args, **kwargs)
    return wrapper


async def require_role(request: Request, allowed_roles: List[str]) -> Tuple[bool, str]:
    """
    Check if the user has one of the allowed roles. Returns (allowed, role).
    """
    user_id = request.headers.get("x-discord-user-id", "unknown")
    username = request.headers.get("x-discord-username", "unknown")
    role = await get_user_role(user_id)
    allowed = role in allowed_roles
    return allowed, role


def with_permission(allowed_roles: List[str]) -> Callable:
    """
    Decorator to enforce allowed roles for an endpoint. Injects user_id_ctx, username, and role.
    """
    def decorator(endpoint: Callable[..., Awaitable[Any]]) -> Callable:
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args else None)
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request object missing",
                )
            user_id, username = extract_discord_headers(request)
            role = await get_user_role(user_id)
            if role not in allowed_roles:
                logger.warning(
                    f"Permission denied for user {user_id} ({username}) with role {role}"
                )
                return {
                    "text": f"Permission denied: requires one of {', '.join(allowed_roles)}."
                }
            kwargs["user_id_ctx"] = user_id  # acting user for audit log
            kwargs["username"] = username
            kwargs["role"] = role
            return await endpoint(*args, **kwargs)
        return wrapper
    return decorator
