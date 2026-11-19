"""
Outbound WhatsApp Cloud API helpers.
In local/demo mode messages are logged instead of sent.
"""

import logging
import httpx
from app.core.config import settings

logger = logging.getLogger("carepath.whatsapp")


async def send_text(to: str, body: str) -> bool:
    """
    Send a plain-text WhatsApp message.
    Returns True on success (or in demo mode when token is missing).
    """
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.info("[DEMO] Would send to %s:\n%s", to, body)
        return True

    url = (
        f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            logger.error("WhatsApp send failed: %s %s", resp.status_code, resp.text)
            return False
        return True


def welcome_message() -> str:
    return (
        "Welcome to CarePath.\n\n"
        "You can use this service to learn about reproductive health and find appropriate care. "
        "It does *not* diagnose medical conditions and does not replace a qualified clinician.\n\n"
        "Before we continue, I need your consent to collect limited information for a private assessment. "
        "You can stop at any time.\n\n"
        "Reply *YES* to continue with a private assessment, or *NO* to exit."
    )


def pathway_choice_message() -> str:
    return (
        "What would you like help with?\n\n"
        "1. General reproductive health\n"
        "2. Fertility concerns\n"
        "3. Symptoms or a health concern\n"
        "4. Find a healthcare professional\n\n"
        "Reply with the number."
    )


def recommendation_message(decision, provider_text: str) -> str:
    factors = "\n".join(f"• {f}" for f in decision.explanation_factors)
    return (
        f"{decision.next_step_summary}\n\n"
        f"*Factors considered:*\n{factors}\n\n"
        f"{decision.screening_disclaimer}\n\n"
        f"*Suggested services / contacts (prototype directory):*\n\n{provider_text}\n\n"
        "If this is an emergency, seek local emergency care immediately.\n\n"
        "Reply *DONE* if you are finished, or *REMIND* if you would like an optional follow-up reminder "
        "(requires separate consent)."
    )


async def send_interactive_buttons(to: str, body: str, buttons: list[dict]) -> bool:
    """
    Send a WhatsApp interactive button message.
    buttons: list of {"id": "...", "title": "..."}  (max 3)
    """
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        titles = " | ".join(b["title"] for b in buttons)
        logger.info("[DEMO] Would send interactive to %s:\n%s\nButtons: %s", to, body, titles)
        return True

    url = (
        f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
                    for b in buttons[:3]
                ]
            },
        },
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            logger.error("WhatsApp interactive send failed: %s %s", resp.status_code, resp.text)
            return False
        return True


def consent_buttons() -> list[dict]:
    return [
        {"id": "yes", "title": "Yes, continue"},
        {"id": "no", "title": "No, exit"},
    ]


def pathway_buttons() -> list[dict]:
    return [
        {"id": "1", "title": "General health"},
        {"id": "2", "title": "Fertility"},
        {"id": "3", "title": "Symptoms"},
    ]
