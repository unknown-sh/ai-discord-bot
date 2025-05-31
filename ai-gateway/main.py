import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from ai_gateway.providers import ask
from ai_gateway.supabase_config import set_config, get_config, get_all_config
from config_engine.help_text import COMMANDS, format_command_help, format_config_help, list_all_configs
# from config_engine.access import get_access_role
from ai_gateway.supabase_roles import get_user_role, set_user_role, get_all_roles
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import sys

log_handler = RotatingFileHandler("bot_actions.log", maxBytes=1024 * 1024, backupCount=5)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(stream_handler)

from common.logging import log_action


app = FastAPI()

# --- MCP server router import and inclusion ---
from mcp_server.router import router as mcp_router
app.include_router(mcp_router)

class MessageRequest(BaseModel):
    message: str

class ConfigUpdate(BaseModel):
    value: str

class RoleUpdate(BaseModel):
    user_id: str
    role: str

@app.get("/acl/role/{user_id}")
def get_user_role_route(user_id: str):
    role = get_user_role(user_id)
    return {"role": role}

# New route to show the role of a specified user
@app.get("/acl/show/{user_id}")
def show_user_role(user_id: str):
    role = get_user_role(user_id)
    return { "user_id": user_id, "role": role }

@app.get("/help")
def help_root(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, "Viewed help root")
    return { "text": (
        "**Bot Help**\n"
        "Commands: " + ", ".join(COMMANDS.keys()) + "\n"
        "Type `@bot help <command>` for details on a command.\n"
        "Type `@bot help config <key>` for config help."
    ) }

@app.get("/help/command/{command}")
def help_command(command: str, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Viewed help for command: {command}")
    return { "text": format_command_help(command) }

@app.get("/help/config/{param}")
def help_config(param: str, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Viewed help for config: {param}")
    return { "text": format_config_help(param) }

@app.get("/help/config")
def help_config_list(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, "Viewed config help list")
    return { "text": "Available config options: " + list_all_configs() }

@app.get("/show/config")
def show_config_list(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["user", "admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only users, admin, or superadmin can view config keys." }
    log_action(user_id, username, "Listed all config keys")
    from config_engine.help_text import CONFIG_HELP
    lines = [f"{k}: {v['desc']}" for k, v in CONFIG_HELP.items()]
    return { "text": "Available config keys:\n" + "\n".join(lines) }

@app.get("/show/config/{key}")
def show_config_key(key: str, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["user", "admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only users, admin, or superadmin can view config values." }
    log_action(user_id, username, f"Showed config value for key: {key}")
    value = get_config(key)
    if value is None:
        return { "text": f"No value set for config key: {key}" }
    return { "text": f"Current value for `{key}`: {value}" }

@app.get("/show/commands")
def show_commands(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["user", "admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only users, admin, or superadmin can view commands." }
    log_action(user_id, username, "Listed all bot commands")
    from config_engine.help_text import COMMANDS
    lines = [f"{k}: {v}" for k, v in COMMANDS.items()]
    return { "text": "Available bot commands:\n" + "\n".join(lines) }

def get_requester_role(request: Request) -> str:
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    return get_user_role(user_id)

def require_role(request: Request, allowed_roles):
    role = get_requester_role(request)
    if role not in allowed_roles:
        return False, role
    return True, role

@app.get("/show/roles")
def show_roles(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["superadmin"])
    if not allowed:
        return { "text": "Permission denied: only superadmin can view all roles." }
    log_action(user_id, username, "Listed all roles")
    roles = get_all_roles()
    if not roles:
        return { "text": "No roles found." }
    lines = [f"{uid}: {role}" for uid, role in roles.items()]
    return { "text": "All user roles:\n" + "\n".join(lines) }

@app.get("/show/role/{user_id}")
def show_role(user_id: str, request: Request):
    requester_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    norm_id = extract_user_id(user_id)
    allowed, role = require_role(request, ["superadmin"])
    # Allow user to see their own role
    if not allowed and norm_id != requester_id:
        return { "text": "Permission denied: only superadmin can view roles for others." }
    log_action(norm_id, username, f"Viewed role for user {user_id}")
    role = get_user_role(norm_id)
    if not role:
        return { "text": f"No role found for user {user_id}." }
    return { "text": f"User {user_id} has role: {role}" }

from ai_gateway.discord_utils import fetch_discord_username

@app.post("/add/role/{user_id}")
def add_role(user_id: str, request: Request):
    requester_id = request.headers.get("X-Discord-User-ID", "unknown")
    actor_username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["superadmin"])
    if not allowed:
        return { "text": "Permission denied: only superadmin can add roles." }
    norm_id = extract_user_id(user_id)
    data = request.json() if hasattr(request, 'json') else {}
    role = data.get("role") if isinstance(data, dict) else None
    # Accept username from request body if provided, else use header, else fetch from Discord
    target_username = data.get("username") if isinstance(data, dict) and data.get("username") else actor_username
    if (not target_username or target_username == "unknown"):
        import os
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        if bot_token:
            target_username = fetch_discord_username(norm_id, bot_token)
        else:
            target_username = "unknown"
    if not role:
        return { "text": "Missing 'role' in request body." }
    log_action(norm_id, actor_username, f"Attempted to add role '{role}' for user {norm_id} ({target_username})")
    set_user_role(norm_id, target_username, role)
    return { "text": f"Role '{role}' added to user {norm_id} ({target_username})." }

@app.post("/remove/role/{user_id}")
def remove_role(user_id: str, request: Request):
    requester_id = request.headers.get("X-Discord-User-ID", "unknown")
    actor_username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["superadmin"])
    if not allowed:
        return { "text": "Permission denied: only superadmin can remove roles." }
    norm_id = extract_user_id(user_id)
    data = request.json() if hasattr(request, 'json') else {}
    target_username = data.get("username") if isinstance(data, dict) and data.get("username") else actor_username
    if (not target_username or target_username == "unknown"):
        import os
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        if bot_token:
            target_username = fetch_discord_username(norm_id, bot_token)
        else:
            target_username = "unknown"
    log_action(norm_id, actor_username, f"Attempted to remove role for user {norm_id} ({target_username})")
    set_user_role(norm_id, target_username, "guest")
    return { "text": f"Role removed for user {norm_id} (set to 'guest')." }

@app.get("/hello")
def hello_bot(request: Request):
    username = request.headers.get("X-Discord-Username", "there")
    return { "text": f"Hello, {username}! I'm your friendly bot. How can I help you today?" }

@app.post("/config/personality")
def config_personality(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only admin and superadmin can modify config." }
    log_action(user_id, username, f"Set personality: {payload.value}")
    set_config("AI_PERSONALITY", payload.value)
    return {"status": "ok"}

@app.post("/config/provider")
def config_provider(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only admin and superadmin can modify config." }
    log_action(user_id, username, f"Set provider: {payload.value}")
    set_config("AI_PROVIDER", payload.value)
    return {"status": "ok"}

@app.post("/config/model")
def config_model(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only admin and superadmin can modify config." }
    log_action(user_id, username, f"Set model: {payload.value}")
    set_config("OPENAI_MODEL", payload.value)
    return {"status": "ok"}

@app.get("/config/status")
def config_status(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, "Checked config status")
    try:
        return get_all_config()
    except Exception:
        fallback_config = {
            "AI_PERSONALITY": os.getenv("AI_PERSONALITY", ""),
            "AI_PROVIDER": os.getenv("AI_PROVIDER", "openai"),
            "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4"),
        }
        return fallback_config

@app.post("/ask")
async def ask_endpoint(request: Request, body: MessageRequest):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    allowed, role = require_role(request, ["user", "admin", "superadmin"])
    if not allowed:
        return { "text": "Permission denied: only users, admin, or superadmin can use @bot commands." }
    log_action(user_id, username, f"Asked: {body.message}")
    try:
        reply = await ask(body.message)
    except TypeError:
        reply = ask(body.message)
    return {"reply": reply}

# --- ACL role set endpoint ---

@app.post("/acl/set")
def set_user_role_route(payload: RoleUpdate, request: Request):
    valid_roles = ["user", "admin", "superadmin"]
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    actor_id = request.headers.get("X-Discord-User-ID", "unknown")
    actor_name = request.headers.get("X-Discord-Username", "unknown")
    log_action(actor_id, actor_name, f"Set role of {payload.user_id} to {payload.role}")

    set_user_role(payload.user_id, "N/A", payload.role)
    return {"status": "ok"}


# Route to list all roles from acl.yaml
@app.get("/acl/all")
def list_all_roles():
    try:
        return get_all_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))