import logging

import aiohttp

UNKNOWN_USERNAME = "unknown"


async def fetch_discord_username(
    user_id: str, bot_token: str, timeout: int = 10
) -> str:
    """
    Asynchronously fetch the username for a Discord user by their user ID using the Discord API.
    Requires a bot token with necessary permissions.
    Returns UNKNOWN_USERNAME on failure.
    """
    url = f"https://discord.com/api/v10/users/{user_id}"
    headers = {"Authorization": f"Bot {bot_token}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("username", UNKNOWN_USERNAME)
                body = await resp.text()
                logging.warning(
                    f"Discord API returned status {resp.status} for user_id {user_id}. Body: {body}"
                )
    except Exception as e:
        logging.error(f"Error fetching Discord username for {user_id}: {e}")
    return UNKNOWN_USERNAME
