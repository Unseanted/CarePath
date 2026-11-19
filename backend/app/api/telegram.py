"""
Telegram webhook + helper endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks, Query
from app.core.config import settings
from app.services.telegram_bot import (
    handle_telegram_update,
    set_webhook,
    delete_webhook,
    get_me,
)

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    """Receive updates from Telegram."""
    if settings.TELEGRAM_WEBHOOK_SECRET and x_telegram_bot_api_secret_token:
        if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Invalid secret token")

    body = await request.json()
    background_tasks.add_task(handle_telegram_update, body)
    return {"ok": True}


@router.post("/set-webhook")
async def telegram_set_webhook(public_base_url: str = Query(..., description="https://your-api.example.com")):
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Only in DEBUG")
    return await set_webhook(public_base_url)


@router.post("/delete-webhook")
async def telegram_delete_webhook():
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Only in DEBUG")
    return await delete_webhook()


@router.get("/me")
async def telegram_me():
    """Check bot token / identity."""
    return await get_me()
