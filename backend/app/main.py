"""
CarePath FastAPI application entry point.
Channels: Web chat (primary) · Telegram · WhatsApp (optional)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import webhook, health, admin, clinician, chat, telegram
from app.core.config import settings
try:
    from app.db.session import init_db
except Exception:
    init_db = None  # type: ignore
from app import __version__

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger("carepath")

logger.warning(
    "CORS allowed origins: %s",
    settings.cors_origins_list,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "CarePath starting – version=%s rules=%s env=%s sqlite=%s cors=%s",
        __version__,
        settings.RULES_VERSION,
        settings.ENVIRONMENT,
        settings.CAREPATH_USE_SQLITE,
        settings.cors_origins_list,
    )
    if init_db:
        try:
            await init_db()
            logger.info("Database tables ready")
        except Exception as exc:
            logger.warning("DB init skipped: %s", exc)
    else:
        logger.info("Running in-memory only (no async DB driver)")
    yield
    logger.info("CarePath shutting down")


app = FastAPI(
    title="CarePath",
    description=(
        "Reproductive health navigation – web chat, Telegram, optional WhatsApp. "
        "Does not diagnose conditions. Clinical rules are provisional."
    ),
    version=__version__,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

# CORS – required for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["web-chat"])
app.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
app.include_router(webhook.router, prefix="/webhook", tags=["whatsapp"])
app.include_router(admin.router, prefix="/admin", tags=["demo"])
app.include_router(clinician.router, prefix="/clinician", tags=["clinician"])
