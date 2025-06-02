import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

LOG_FILE = os.getenv(
    "LOG_FILE", "logs/bot_actions.log"
)  # Use logs/ instead of ../logs/
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))  # 5 MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Attempt file handler
try:
    # Try to open the file for appending to check writeability
    with open(LOG_FILE, "a"):
        pass
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except Exception as e:
    # Fallback to stdout
    fallback_handler = logging.StreamHandler(sys.stdout)
    fallback_handler.setFormatter(formatter)
    logger.addHandler(fallback_handler)
    logger.warning(
        f"Failed to initialize file-based logging: {e}. Using stdout fallback."
    )

# --- Supabase logging handler ---
try:
    from ai_gateway.supabase_client import supabase
except ImportError:
    supabase = None

import asyncio


class SupabaseLogHandler(logging.Handler):
    """
    Async logging handler for Supabase. Uses asyncio.to_thread to avoid blocking the event loop.

    This handler logs messages to Supabase asynchronously, ensuring that the event loop remains unblocked.
    If Supabase is not available, the handler will silently ignore the log message.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to Supabase.

        Args:
            record: The log record to emit.
        """
        if supabase is None:
            return
        try:
            msg = self.format(record)
            extra = getattr(record, "extra", {})
            user_id = extra.get("user_id", None)
            username = extra.get("username", None)
            action = extra.get("action", None)
            # Proper async scheduling for coroutine
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._log_to_supabase(user_id, username, action))
            except RuntimeError:
                # No running event loop (e.g. called from sync context at startup)
                asyncio.run(self._log_to_supabase(user_id, username, action))
        except Exception as e:
            print(
                f"[SupabaseLogHandler] Failed to log to Supabase: {e}", file=sys.stderr
            )

    async def _log_to_supabase(self, user_id: str, username: str, action: str) -> None:
        """
        Log a message to Supabase asynchronously.

        Args:
            user_id: The user ID performing the action.
            username: The username of the user.
            action: The action performed.
        """
        try:
            await asyncio.to_thread(
                lambda: supabase.table("bot_logs")
                .insert(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_id": user_id,
                        "username": username,
                        "action": action,
                    }
                )
                .execute()
            )
        except Exception as e:
            print(
                f"[SupabaseLogHandler] Async log to Supabase failed: {e}",
                file=sys.stderr,
            )


supabase_handler = SupabaseLogHandler()
supabase_handler.setFormatter(formatter)
logger.addHandler(supabase_handler)


async def log_action(user_id: str, action_type: str, data: str, username: Optional[str] = None) -> None:
    """
    Asynchronously log a user action to file/stdout and Supabase.

    Args:
        user_id: The user ID performing the action.
        action_type: The type of action performed.
        data: Additional data about the action.
        username: Optional username of the user.
    Returns:
        None
    """
    message = f"User ID: {user_id} | Username: {username} | Action: {action_type} | Data: {data}"
    # Use asyncio.to_thread to avoid blocking if logger handlers are sync
    await asyncio.to_thread(
        logger.info,
        message,
        extra={
            "extra": {
                "user_id": user_id,
                "username": username,
                "action": f"{action_type}: {data}",
            }
        },
    )
