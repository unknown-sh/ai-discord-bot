from ai_gateway.decorators import with_discord_headers
from fastapi import APIRouter, Request

from common.custom_logging import log_action
from config_engine.help_text import (COMMANDS, format_command_help,
                                     format_config_help, list_all_configs)

router = APIRouter()


@router.get("/help")
async def help_root(request: Request, user_id=None, username=None) -> dict:
    await log_action(user_id, username, "Viewed help root")
    return {
        "text": (
            "**Bot Help**\n"
            "Commands: " + ", ".join(COMMANDS.keys()) + "\n"
            "Type `@bot help <command>` for details on a command.\n"
            "Type `@bot help config <key>` for config help."
        )
    }


@router.get("/help/command/{command}")
async def help_command(
    command: str, request: Request, user_id=None, username=None
) -> dict:
    await log_action(user_id, username, f"Viewed help for command: {command}")
    return {"text": format_command_help(command)}


@router.get("/help/config/{param}")
async def help_config(
    param: str, request: Request, user_id=None, username=None
) -> dict:
    await log_action(user_id, username, f"Viewed help for config: {param}")
    return {"text": format_config_help(param)}


@router.get("/help/config")
async def help_config_list(request: Request, user_id=None, username=None) -> dict:
    await log_action(user_id, username, "Viewed config help list")
    return {"text": "Available config options: " + list_all_configs()}
