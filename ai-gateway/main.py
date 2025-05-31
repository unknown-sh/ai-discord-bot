import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from ai_gateway.providers import ask
from ai_gateway.supabase_config import set_config, get_config, get_all_config
from config_engine.help_text import COMMANDS, COMMAND_HELP, CONFIG_HELP
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
async def help_root(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, "Viewed help root")
    return { "text": "Commands: " + ", ".join(COMMANDS.keys()) }

@app.get("/help/command/{command}")
async def help_command(command: str, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Viewed help for command: {command}")
    return { "text": COMMAND_HELP.get(command, "No help found for this command.") }

@app.get("/help/config/{param}")
async def help_config(param: str, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Viewed help for config: {param}")
    info = CONFIG_HELP.get(param)
    if not info:
        return { "text": "Unknown config key." }
    return { "text": f"**{param}**: {info['desc']}\nUsage: `{info['usage']}`" }

@app.post("/config/personality")
def config_personality(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Set personality: {payload.value}")
    set_config("AI_PERSONALITY", payload.value)
    return {"status": "ok"}

@app.post("/config/provider")
def config_provider(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Set provider: {payload.value}")
    set_config("AI_PROVIDER", payload.value)
    return {"status": "ok"}

@app.post("/config/model")
def config_model(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
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