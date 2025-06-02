"""
Supabase async client singleton for use throughout the backend.
Reads SUPABASE_URL and SUPABASE_KEY from environment.

Exports:
    supabase: Optional[AsyncClient] — the initialized Supabase client or None if config is missing/invalid.
"""

import logging
import os
from typing import Optional

from supabase import AsyncClient, create_client

SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

supabase: Optional[AsyncClient] = None
"""
Singleton Supabase client instance for async database operations.
Access as ai_gateway.supabase_client.supabase.
Returns None if credentials are missing or initialization fails.
"""

if not SUPABASE_URL or not SUPABASE_KEY:
    logging.warning(
        "[Supabase] SUPABASE_URL or SUPABASE_KEY not set — Supabase disabled"
    )
else:
    try:
        # Remove client_class argument for compatibility
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("[Supabase] Client initialized successfully")
    except Exception as e:
        logging.error(f"[Supabase] Failed to create client: {e}")
        supabase = None
