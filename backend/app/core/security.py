"""Lightweight security helpers for the prototype."""

import hashlib
import hmac
from app.core.config import settings


def hash_phone(phone: str) -> str:
    """
    Create a stable opaque identifier from a WhatsApp phone number.
    Do not store raw phone numbers in application logs or free-text fields.
    """
    return hmac.new(
        settings.SECRET_KEY.encode(),
        phone.encode(),
        hashlib.sha256,
    ).hexdigest()[:32]


def verify_webhook_signature(payload: bytes, signature_header: str | None) -> bool:
    """
    Placeholder for Meta's X-Hub-Signature-256 verification.
    Implement fully before production use.
    """
    if not signature_header or not settings.WHATSAPP_ACCESS_TOKEN:
        # In local/dev mode allow through when token is not configured
        return settings.DEBUG
    # Production implementation would compute HMAC-SHA256 of payload
    # with the app secret and compare to the header value.
    return True
