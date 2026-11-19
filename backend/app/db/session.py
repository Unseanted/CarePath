"""Async DB session – optional. Prototype works fully in-memory without this."""
from collections.abc import AsyncGenerator

try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from app.core.config import settings
    from app.models.orm import Base

    engine = create_async_engine(
        settings.effective_database_url,
        echo=False,
        future=True,
    )
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def init_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

except Exception as _exc:  # noqa: BLE001
    async_session_factory = None  # type: ignore
    get_session = None  # type: ignore

    async def init_db() -> None:  # type: ignore
        return None
