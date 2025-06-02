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


async def get_config(key: str) -> str:
    """
    Asynchronously fetch a config value from Supabase, falling back to environment variable if not found.
    Sensitive values are masked in logs.
    Returns the config value as a string (may be None if not found).
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
        if data:
            value = data[0]["value"]
            masked = mask_value(key, value)
            logging.info(f"[Supabase] Fetched config key '{key}': '{masked}'")
            return value
        fallback = os.getenv(key)
        masked = mask_value(key, fallback)
        logging.info(
            f"[Supabase Fallback] No value for key '{key}' in DB; using .env fallback: '{masked}'"
        )
        return fallback
    except Exception as e:
        fallback = os.getenv(key)
        masked = mask_value(key, fallback)
        logging.warning(
            f"[Supabase Fallback] Failed to fetch config for key '{key}': {str(e)} — using fallback: '{masked}'"
        )
        return fallback


async def get_all_config() -> dict[str, str]:
    """
    Asynchronously fetch all config values from Supabase, masking sensitive ones.
    Returns a dict of config keys to masked values.
    """
    try:
        res = await asyncio.to_thread(
            lambda: supabase.table("bot_config").select("*").execute()
        )
        data = res.data
        if data:
            config = {row["key"]: mask_value(row["key"], row["value"]) for row in data}
            logging.info(f"[Supabase] Fetched all config: {config}")
            return config
        logging.info("[Supabase] No config found in DB.")
        return {}
    except Exception as e:
        logging.error(f"[Supabase Error] Failed to fetch all config: {str(e)}")
        return {}
