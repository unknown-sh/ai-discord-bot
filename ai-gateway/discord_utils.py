import requests

def fetch_discord_username(user_id: str, bot_token: str) -> str:
    """
    Fetch the username for a Discord user by their user ID using the Discord API.
    Requires a bot token with necessary permissions.
    """
    url = f"https://discord.com/api/v10/users/{user_id}"
    headers = {
        "Authorization": f"Bot {bot_token}"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("username", "unknown")
    return "unknown"
