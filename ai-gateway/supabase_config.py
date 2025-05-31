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

def set_config(key: str, value: str):
    if key not in ALLOWED_KEYS:
        raise ValueError(f"Invalid config key: {key}")
    try:
        supabase.table("bot_config").upsert({"key": key, "value": value}).execute()
        logging.info(f"[Supabase] Config set for key '{key}' to value '{value}'")
    except Exception as e:
        logging.error(f"[Supabase Error] Failed to set config for key '{key}': {str(e)}")
        raise

SENSITIVE_KEYS = {"OPENAI_API_KEY", "SUPABASE_KEY", "ANTHROPIC_API_KEY", "MISTRAL_API_KEY"}

def mask_value(key, value):
    if key in SENSITIVE_KEYS and value:
        return value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
    return value

def get_config(key: str) -> str:
    try:
        res = supabase.table("bot_config").select("value").eq("key", key).limit(1).execute()
        data = res.data
        if data:
            value = data[0]["value"]
            masked = mask_value(key, value)
            logging.info(f"[Supabase] Fetched config key '{key}': '{masked}'")
            return value
        fallback = os.getenv(key)
        masked = mask_value(key, fallback)
        logging.info(f"[Supabase Fallback] No value for key '{key}' in DB; using .env fallback: '{masked}'")
        return fallback
    except Exception as e:
        fallback = os.getenv(key)
        masked = mask_value(key, fallback)
        logging.warning(f"[Supabase Fallback] Failed to fetch config for key '{key}': {str(e)} — using fallback: '{masked}'")
        return fallback

def get_all_config() -> dict:
    try:
        res = supabase.table("bot_config").select("*").execute()
        logging.info("[Supabase] Fetched all config values from database")
        return {row["key"]: row["value"] for row in res.data}
    except Exception as e:
        logging.warning(f"[Supabase Fallback] Failed to fetch all config values: {str(e)} — falling back to .env")
        fallback_config = {key: os.getenv(key) for key in ALLOWED_KEYS}
        return fallback_config