from ai_gateway.supabase import supabase
import os
import logging

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
    "MISTRAL_BASE_URL"
}

async def set_config(key: str, value: str):
    if key not in ALLOWED_KEYS:
        raise ValueError(f"Invalid config key: {key}")
    try:
        await supabase.table("bot_config").upsert({"key": key, "value": value}).execute()
        logging.info(f"[Supabase] Config set for key '{key}' to value '{value}'")
    except Exception as e:
        logging.error(f"[Supabase Error] Failed to set config for key '{key}': {str(e)}")
        raise

async def get_config(key: str) -> str:
    try:
        res = await supabase.table("bot_config").select("value").eq("key", key).limit(1).execute()
        data = res.data
        if data:
            value = data[0]["value"]
            logging.info(f"[Supabase] Fetched config key '{key}': '{value}'")
            return value
        fallback = os.getenv(key)
        logging.info(f"[Supabase Fallback] No value for key '{key}' in DB; using .env fallback: '{fallback}'")
        return fallback
    except Exception as e:
        fallback = os.getenv(key)
        logging.warning(f"[Supabase Fallback] Failed to fetch config for key '{key}': {str(e)} — using fallback: '{fallback}'")
        return fallback

async def get_all_config() -> dict:
    try:
        res = await supabase.table("bot_config").select("*").execute()
        logging.info("[Supabase] Fetched all config values from database")
        return {row["key"]: row["value"] for row in res.data}
    except Exception as e:
        logging.warning(f"[Supabase Fallback] Failed to fetch all config values: {str(e)} — falling back to .env")
        fallback_config = {key: os.getenv(key) for key in ALLOWED_KEYS}
        return fallback_config