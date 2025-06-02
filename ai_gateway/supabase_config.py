import logging
import os

from ai_gateway.supabase_client import supabase

from common.utils import mask_value

ALLOWED_KEYS = {
    "AI_PROVIDER",
    "OPENAI_MODEL",
    "OPENAI_TEMPERATURE",
    "AI_PERSONALITY",
    "OPENAI_MAX_TOKENS",
    "OPENAI_TOP_P",
    "OPENAI_PRESENCE_PENALTY",
    "OPENAI_FREQUENCY_PENALTY",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_TEMPERATURE",
    "ANTHROPIC_MAX_TOKENS",
    "MISTRAL_MODEL",
    "MISTRAL_TEMPERATURE",
    "MISTRAL_MAX_TOKENS",
    "MISTRAL_BASE_URL",
}

from common.utils import SENSITIVE_KEYS, mask_value

import asyncio




async def set_config(key: str, value: str) -> None:
    """
    Asynchronously set a config value in Supabase for a given key.
    Only allows keys in ALLOWED_KEYS. Logs and masks sensitive values.
    """
    if key not in ALLOWED_KEYS:
        raise ValueError(f"Invalid config key: {key}")
    try:
        await asyncio.to_thread(
            lambda: supabase.table("bot_config")
            .upsert({"key": key, "value": value})
            .execute()
        )
        logging.info(
            f"[Supabase] Config set for key '{key}' to value '{mask_value(key, value)}'"
        )
    except Exception as e:
        logging.error(
            f"[Supabase Error] Failed to set config for key '{key}': {str(e)}"
        )
        raise


async def get_config(key: str, role: str = None) -> str:
    """
    Asynchronously fetch a config value from Supabase, falling back to environment variable if not found.
    Sensitive values are masked in logs and only shown unmasked to superadmin via explicit request.
    Returns the config value as a string (masked or None if not found).
    """
    try:
        res = await asyncio.to_thread(
            lambda: supabase.table("bot_config")
            .select("value")
            .eq("key", key)
            .limit(1)
            .execute()
        )
        data = res.data
        value = None
        if data:
            value = data[0]["value"]
        # Patch: Always fallback to env if value is None or empty for sensitive keys
        if key in SENSITIVE_KEYS:
            if value:
                if role == "superadmin":
                    logging.info(f"[Supabase] Fetched config key '{key}': '{mask_value(key, value)}'")
                return value
            fallback = os.getenv(key)
            logging.warning(f"[Supabase Fallback] Sensitive key '{key}' missing or empty in DB; using .env fallback: '{mask_value(key, fallback)}'")
            return fallback
        # For non-sensitive keys
        if value:
            logging.info(f"[Supabase] Fetched config key '{key}': '{mask_value(key, value)}'")
            return value
        fallback = os.getenv(key)
        logging.info(f"[Supabase Fallback] No value for key '{key}' in DB; using .env fallback: '{mask_value(key, fallback)}'")
        return fallback
    except Exception as e:
        fallback = os.getenv(key)
        if key in SENSITIVE_KEYS and role != "superadmin":
            return None
        logging.warning(
            f"[Supabase Fallback] Failed to fetch config for key '{key}': {str(e)} — using fallback: '{mask_value(key, fallback)}'"
        )
        return fallback


async def get_all_config(role: str = None) -> dict[str, str]:
    """
    Asynchronously fetch all config values from Supabase, masking or omitting sensitive ones.
    Returns a dict of config keys to masked values for admins, or all for superadmin (masked in bulk).
    """
    try:
        res = await asyncio.to_thread(
            lambda: supabase.table("bot_config").select("*").execute()
        )
        data = res.data
        config = {}
        if data:
            for row in data:
                key = row["key"]
                value = row["value"]
                if key in SENSITIVE_KEYS:
                    if role == "superadmin":
                        config[key] = mask_value(key, value)
                    else:
                        # Hide from admin in bulk listing
                        continue
                else:
                    config[key] = value
            logging.info(f"[Supabase] Fetched all config (role={role}): {config}")
            return config
        logging.info("[Supabase] No config found in DB.")
        return {}
    except Exception as e:
        logging.error(f"[Supabase Error] Failed to fetch all config: {str(e)}")
        return {}
