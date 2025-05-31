from .supabase import supabase

def set_config(key: str, value: str):
    supabase.table("config").upsert({"key": key, "value": value}).execute()

def get_config(key: str) -> str:
    res = supabase.table("config").select("value").eq("key", key).limit(1).execute()
    data = res.data
    return data[0]["value"] if data else ""

def get_all_config() -> dict:
    res = supabase.table("config").select("*").execute()
    return {row["key"]: row["value"] for row in res.data}