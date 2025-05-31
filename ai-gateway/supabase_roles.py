from .supabase import supabase

async def get_user_role(user_id: str) -> str:
    result = supabase.table("roles").select("role").eq("user_id", user_id).execute()
    data = result.data
    if not data:
        return "guest"
    return data[0]["role"]

async def set_user_role(user_id: str, username: str, role: str):
    supabase.table("roles").upsert({
        "user_id": user_id,
        "username": username,
        "role": role
    }).execute()

async def get_all_roles():
    result = supabase.table("roles").select("*").execute()
    return result.data