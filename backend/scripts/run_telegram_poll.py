#!/usr/bin/env python3
"""
Long-polling Telegram bot runner.
Use this when you don't have a public HTTPS URL for webhooks.

  export TELEGRAM_BOT_TOKEN=...
  python scripts/run_telegram_poll.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
from app.core.config import settings
from app.services.telegram_bot import handle_telegram_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("carepath.tg_poll")

API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN in .env")
        sys.exit(1)

    # Clear any existing webhook so polling works
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(f"{API}/deleteWebhook")
        me = (await client.get(f"{API}/getMe")).json()
        if not me.get("ok"):
            print("Invalid token:", me)
            sys.exit(1)
        print(f"Bot online: @{me['result'].get('username')} – long polling…")

        offset = 0
        while True:
            try:
                resp = await client.get(
                    f"{API}/getUpdates",
                    params={"offset": offset, "timeout": 25},
                    timeout=35,
                )
                data = resp.json()
                for upd in data.get("result") or []:
                    offset = max(offset, upd["update_id"] + 1)
                    try:
                        await handle_telegram_update(upd)
                    except Exception as exc:
                        logger.exception("Update failed: %s", exc)
            except Exception as exc:
                logger.warning("Poll error: %s – retrying", exc)
                await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
