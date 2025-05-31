from supabase import create_client, AsyncClient, Client
import os
import logging

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: AsyncClient | Client = None

if not SUPABASE_URL or not SUPABASE_KEY:
    logging.warning(
        "[Supabase] SUPABASE_URL or SUPABASE_KEY not set — Supabase disabled"
    )
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("[Supabase] Client initialized successfully")
    except Exception as e:
        logging.error(f"[Supabase] Failed to create client: {e}")
        supabase = None
