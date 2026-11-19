"""
Telegram Bot channel for CarePath.
Uses long-polling in a background task OR webhook at /telegram/webhook.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.conversation import process_message, _get_or_create_session

logger = logging.getLogger("carepath.telegram")

API_BASE = "https://api.telegram.org"


async def send_telegram_message(chat_id: int | str, text: str) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set – cannot send")
        return False
    url = f"{API_BASE}/bot{token}/sendMessage"
    # Telegram max message length ~4096
    chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)] or [text]
    async with httpx.AsyncClient(timeout=30) as client:
        for chunk in chunks:
            resp = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "HTML",
                },
            )
            if resp.status_code >= 400:
                # Retry without parse_mode if HTML fails
                resp = await client.post(
                    url,
                    json={"chat_id": chat_id, "text": chunk},
                )
                if resp.status_code >= 400:
                    logger.error("Telegram send failed: %s %s", resp.status_code, resp.text)
                    return False
    return True


async def handle_telegram_update(update: dict[str, Any]) -> None:
    """Process one Telegram Update object."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()
    if not chat_id or not text:
        return

    # Commands
    if text.startswith("/start"):
        text = "hello"
    elif text.startswith("/stop"):
        text = "stop"
    elif text.startswith("/restart"):
        text = "restart"

    channel_key = f"tg:{chat_id}"
    session = _get_or_create_session(channel_key)
    reply = await process_message(session, text)
    if reply:
        # Strip WhatsApp-style *bold* for cleaner Telegram plain text
        clean = reply.replace("*", "")
        await send_telegram_message(chat_id, clean)


async def set_webhook(public_base_url: str) -> dict:
    """Register webhook with Telegram. public_base_url e.g. https://api.example.com"""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not set"}
    webhook_url = f"{public_base_url.rstrip('/')}/telegram/webhook"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{API_BASE}/bot{token}/setWebhook",
            json={
                "url": webhook_url,
                "secret_token": settings.TELEGRAM_WEBHOOK_SECRET,
                "allowed_updates": ["message"],
            },
        )
        return resp.json()


async def delete_webhook() -> dict:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return {"ok": False}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{API_BASE}/bot{token}/deleteWebhook")
        return resp.json()


async def get_me() -> dict:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return {"ok": False, "error": "no token"}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{API_BASE}/bot{token}/getMe")
        return resp.json()
