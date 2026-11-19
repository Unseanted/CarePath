from fastapi import APIRouter
from app import __version__
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "carepath",
        "version": __version__,
        "rules_version": settings.RULES_VERSION,
        "environment": settings.ENVIRONMENT,
    }
