"""
WhatsApp Cloud API webhook endpoints.
Handles Meta verification challenge and incoming messages.
"""

from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks
from app.core.config import settings
from app.services.conversation import handle_incoming_message

router = APIRouter()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta webhook verification handshake."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """
    Receive incoming WhatsApp messages.
    Respond 200 quickly; process asynchronously.
    """
    body = await request.json()

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
    except (IndexError, AttributeError, KeyError, TypeError):
        return {"status": "ignored"}

    if not messages:
        return {"status": "no_message"}

    for msg in messages:
        background_tasks.add_task(handle_incoming_message, msg, value)

    return {"status": "received"}
