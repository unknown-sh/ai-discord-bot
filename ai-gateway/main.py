from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from providers import ask
from config_engine.runtime_state import (
    set_personality, set_provider, set_model, get_provider, get_model, get_personality
)
from config_engine.help_text import COMMANDS, COMMAND_HELP, CONFIG_HELP
# from config_engine.access import get_access_role
from supabase_roles import get_user_role, set_user_role, get_all_roles
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

log_handler = RotatingFileHandler("bot_actions.log", maxBytes=1024 * 1024, backupCount=5)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def log_action(user_id: str, username: str, action: str):
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"{timestamp} - {username} ({user_id}) - {action}")

app = FastAPI()

class MessageRequest(BaseModel):
    message: str

class ConfigUpdate(BaseModel):
    value: str

class RoleUpdate(BaseModel):
    user_id: str
    role: str

@app.get("/acl/role/{user_id}")
async def get_user_role(user_id: str):
    return {"role": get_access_role(user_id)}

# New route to show the role of a specified user
@app.get("/acl/show/{user_id}")
async def show_user_role(user_id: str):
    role = get_access_role(user_id)
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
async def config_personality(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Set personality: {payload.value}")
    set_personality(payload.value)
    return {"status": "ok"}

@app.post("/config/provider")
async def config_provider(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Set provider: {payload.value}")
    set_provider(payload.value, None)
    return {"status": "ok"}

@app.post("/config/model")
async def config_model(payload: ConfigUpdate, request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Set model: {payload.value}")
    set_provider(get_provider(), payload.value)
    return {"status": "ok"}

@app.get("/config/status")
async def config_status(request: Request):
    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, "Checked config status")
    return {
        "provider": get_provider(),
        "model": get_model(),
        "personality": get_personality()
    }

@app.post("/ask")
async def ask_endpoint(request: MessageRequest):
    reply = ask(request.message)
    return {"reply": reply}

# --- ACL role set endpoint ---
import yaml

@app.post("/acl/set")
async def set_user_role(payload: RoleUpdate, request: Request):
    valid_roles = ["user", "admin", "superadmin"]
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    user_id = request.headers.get("X-Discord-User-ID", "unknown")
    username = request.headers.get("X-Discord-Username", "unknown")
    log_action(user_id, username, f"Set role of {payload.user_id} to {payload.role}")

    try:
        with open("config-engine/acl.yaml", "r") as f:
            acl = yaml.safe_load(f)

        # Remove user_id from all roles
        for role in valid_roles:
            acl.setdefault(role, [])
            acl[role] = [uid for uid in acl[role] if uid != payload.user_id]

        # Add to new role
        acl[payload.role].append(payload.user_id)

        with open("config-engine/acl.yaml", "w") as f:
            yaml.safe_dump(acl, f)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to list all roles from acl.yaml
@app.get("/acl/all")
async def list_all_roles():
    try:
        with open("config-engine/acl.yaml", "r") as f:
            acl = yaml.safe_load(f)
        return acl
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))