"""
Main FastAPI application for AI Gateway.
- Registers all routers (modular, MCP, context)
- Sets up global error middleware
- Provides healthcheck endpoint
- Adds audit logging for all config/admin endpoints
"""

import os

from ai_gateway.audit_helpers import log_audit_event
from ai_gateway.context_memory import router as context_memory_router
from ai_gateway.error_middleware import GlobalErrorMiddleware
from ai_gateway.routers import ask, config, help, roles
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config_engine.access import get_user_role
from mcp_server.router import router as mcp_router

# --- App creation ---
app = FastAPI()
app.add_middleware(GlobalErrorMiddleware)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:51892"],  # Your frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Healthcheck endpoint ---
@app.get("/healthz")
async def healthz() -> dict:
    """Healthcheck endpoint for Docker/infra."""
    return {"status": "ok"}


# --- Router registrations ---
app.include_router(help.router)
app.include_router(config.router)
app.include_router(roles.router)
app.include_router(ask.router)
app.include_router(context_memory_router)

# 4. Auth router (Discord OAuth2)
from ai_gateway.auth import router as auth_router

app.include_router(auth_router)

# 4. MCP router
app.include_router(mcp_router, prefix="/mcp")

# 5. Audit log router
from ai_gateway.audit import router as audit_router

app.include_router(audit_router, prefix="/audit")


# --- Pydantic models ---
class MessageRequest(BaseModel):
    message: str


class ConfigUpdate(BaseModel):
    value: str


class RoleUpdate(BaseModel):
    user_id: str
    role: str


# --- Example endpoints below (add more as needed) ---


@app.get("/acl/role/{user_id}")
async def get_user_role_route(user_id: str, request: Request) -> dict:
    """
    Retrieve the role for a given user and log the audit event.
    """
    role = await get_user_role(user_id)
    await log_audit_event(
        user_id,
        "view_role",
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"role": role}


@app.post("/acl/set")
async def set_user_role_route(payload: RoleUpdate, request: Request) -> dict:
    """
    Set the role for a user and log the audit event.
    """
    valid_roles = ["user", "admin", "superadmin"]
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    actor_id = request.headers.get("X-Discord-User-ID", "unknown")
    actor_name = request.headers.get("X-Discord-Username", "unknown")
    await log_audit_event(
        actor_id,
        f"set_role:{payload.role}",
        username=actor_name,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await set_user_role(payload.user_id, "N/A", payload.role)
    return {"status": "ok"}


@app.get("/acl/all")
async def list_all_roles_route(request: Request) -> dict:
    """
    List all user roles and log the audit event.
    """
    try:
        roles = await get_all_roles()
        await log_audit_event(
            None,
            "view_all_roles",
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug-root")
async def debug_root():
    print("[DEBUG] /debug-root handler invoked")
    return {"status": "ok", "message": "debug-root reached"}


@app.on_event("startup")
async def list_routes():
    print("=== Registered Routes ===")
    for route in app.routes:
        print(f"{route.path} -> {getattr(route, 'endpoint', None)}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "ai_gateway.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
