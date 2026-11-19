from functools import lru_cache
import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")

        ENVIRONMENT: str = "development"
        DEBUG: bool = True
        CAREPATH_USE_SQLITE: bool = True
        DATABASE_URL: str = "postgresql+asyncpg://carepath:carepath@localhost:5432/carepath"
        SQLITE_URL: str = "sqlite+aiosqlite:///./carepath_demo.db"

        # WhatsApp (optional – kept for later)
        WHATSAPP_VERIFY_TOKEN: str = "carepath-verify-token-change-me"
        WHATSAPP_ACCESS_TOKEN: str = ""
        WHATSAPP_PHONE_NUMBER_ID: str = ""
        WHATSAPP_API_VERSION: str = "v21.0"

        # Telegram
        TELEGRAM_BOT_TOKEN: str = ""
        TELEGRAM_WEBHOOK_SECRET: str = "carepath-tg-secret"

        # Web / CORS
        CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001"

        SECRET_KEY: str = "change-me-in-production-use-secrets-manager"
        RULES_VERSION: str = "2026-11-prototype-v0.1"
        CONSENT_VERSION: str = "2026-11-v1"
        CLINICIAN_API_KEY: str = "carepath-clinician-dev-key"

        @property
        def effective_database_url(self) -> str:
            if self.CAREPATH_USE_SQLITE:
                return self.SQLITE_URL
            return self.DATABASE_URL

        @property
        def cors_origins_list(self) -> list[str]:
            return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

except ImportError:
    class Settings:  # type: ignore
        ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        DEBUG = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")
        CAREPATH_USE_SQLITE = os.getenv("CAREPATH_USE_SQLITE", "1") in ("1", "true", "yes")
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://carepath:carepath@localhost:5432/carepath")
        SQLITE_URL = os.getenv("SQLITE_URL", "sqlite+aiosqlite:///./carepath_demo.db")
        WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "carepath-verify-token-change-me")
        WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0")
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "carepath-tg-secret")
        CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-use-secrets-manager")
        RULES_VERSION = os.getenv("RULES_VERSION", "2026-11-prototype-v0.1")
        CONSENT_VERSION = os.getenv("CONSENT_VERSION", "2026-11-v1")
        CLINICIAN_API_KEY = os.getenv("CLINICIAN_API_KEY", "carepath-clinician-dev-key")

        @property
        def effective_database_url(self) -> str:
            if self.CAREPATH_USE_SQLITE:
                return self.SQLITE_URL
            return self.DATABASE_URL

        @property
        def cors_origins_list(self) -> list[str]:
            return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
