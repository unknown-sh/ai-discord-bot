from ai_gateway.audit_helpers import log_audit_event
from ai_gateway.decorators import with_permission
from ai_gateway.providers import ask
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class MessageRequest(BaseModel):
    message: str


@router.post("/ask")
@with_permission(["user", "admin", "superadmin"])
async def ask_endpoint(
    request: Request, body: MessageRequest, user_id=None, user_id_ctx=None, username=None, role=None
) -> dict:
    user_id = user_id or user_id_ctx
    await log_audit_event(
        user_id,
        "ask",
        username=username,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    try:
        reply = await ask(body.message)
    except Exception as e:
        reply = f"Sorry, I couldn't generate a response: {e}"
    if not reply or not str(reply).strip():
        reply = "Sorry, I couldn't generate a response."
    return {"reply": reply}
