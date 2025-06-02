from ai_gateway.audit_helpers import log_audit_event
from ai_gateway.decorators import with_discord_headers, with_permission
from ai_gateway.supabase_roles import (get_all_roles, get_user_role,
                                       set_user_role)
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class RoleUpdate(BaseModel):
    user_id: str
    role: str


@router.get("/acl/role/{user_id}")
@with_permission(["admin", "superadmin"])
async def get_user_role_route(
    user_id: str, request: Request, user_id_ctx=None, username=None, role=None
) -> dict:
    result = await get_user_role(user_id)
    await log_audit_event(
        user_id_ctx,
        f"view_role:{user_id}",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"role": result}


@router.get("/acl/show/{user_id}")
@with_permission(["admin", "superadmin"])
async def show_user_role(
    user_id: str, request: Request, user_id_ctx=None, username=None, role=None
) -> dict:
    result = await get_user_role(user_id)
    await log_audit_event(
        user_id_ctx,
        f"show_user_role:{user_id}",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"user_id": user_id, "role": result}


@router.post("/acl/set")
@with_permission(["admin", "superadmin"])
async def set_user_role_route(
    payload: RoleUpdate, request: Request, user_id_ctx=None, username=None, role=None
):
    valid_roles = ["user", "admin", "superadmin"]
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    await log_audit_event(
        user_id_ctx,
        f"set_role:{payload.role}",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await set_user_role(payload.user_id, "N/A", payload.role)
    return {"status": "ok"}


@router.get("/acl/all")
@with_permission(["admin", "superadmin"])
async def list_all_roles(request: Request, user_id_ctx=None, username=None, role=None):
    try:
        roles = await get_all_roles()
        await log_audit_event(
            user_id_ctx,
            "view_all_roles",
            username=username,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
