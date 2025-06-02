import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, Union

SENSITIVE_KEYS = {
    "OPENAI_API_KEY",
    "SUPABASE_KEY",
    "ANTHROPIC_API_KEY",
    "MISTRAL_API_KEY",
}


# --- General helpers ---
def format_user_tag(username: str, user_id: int) -> str:
    """
    Format a Discord user tag for display.
    """
    return f"@{username} ({user_id})"


def parse_command(content: str) -> tuple[str, list[str]]:
    """
    Parse a command string into a command and argument list.
    Returns (command, args).
    """
    parts = content.strip().split()
    command = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command.lower(), args


def safe_json_dumps(data: Any) -> str:
    """
    Safely dump data to JSON, handling unserializable objects.
    Returns a JSON string or '[Unserializable data]'.
    """
    try:
        return json.dumps(data, indent=2)
    except Exception:
        return "[Unserializable data]"


def normalize_discord_id(user_id: Union[str, int]) -> str:
    """
    Normalize a Discord user ID by stripping whitespace and mention syntax.
    Returns the ID as a string.
    """
    return str(user_id).strip("<>@! ")


def current_timestamp() -> str:
    """
    Get the current UTC timestamp as an ISO8601 string.
    """
    return datetime.utcnow().isoformat()


async def try_or_log(coro, fallback: Any = None) -> Any:
    """
    Await a coroutine, logging any exception and returning a fallback value.
    Args:
        coro: The coroutine to await.
        fallback: Value to return if an exception occurs.
    Returns:
        The result of the coroutine, or fallback if an error occurs.
    """
    try:
        return await coro
    except Exception as e:
        logging.error(f"[utils.try_or_log] Error: {e}")
        return fallback


# --- Security and validation helpers ---
def mask_value(key: str, value: str) -> str:
    """
    Mask sensitive config values for logging or display.
    For sensitive keys, returns partial mask (e.g., sk-****23) if value is long enough, else '****'.
    Otherwise returns the value as-is.
    """
    if key in SENSITIVE_KEYS and value:
        if len(value) > 8:
            return value[:3] + "****" + value[-2:]
        return "****"
    return value


def is_valid_discord_id(user_id: str) -> bool:
    """
    Check if a Discord user ID is valid (numeric, 17-20 digits typical).
    """
    return bool(re.fullmatch(r"\d{17,20}", str(user_id).strip()))


# --- Dict helpers ---
def dict_diff(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a dict of keys/values that differ between two dicts.
    """
    return {k: new[k] for k in new if old.get(k) != new[k]}


def safe_get(d: Dict, *keys, default=None):
    """
    Safely get a nested value from a dict, returning default if any key is missing.
    """
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d
