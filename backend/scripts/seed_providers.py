#!/usr/bin/env python3
"""Seed the simulated provider directory into the database (optional)."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.session import init_db, async_session_factory
from app.models.orm import ProviderORM
from app.services.providers import SIMULATED_PROVIDERS


async def main() -> None:
    await init_db()
    async with async_session_factory() as session:
        for p in SIMULATED_PROVIDERS:
            existing = await session.get(ProviderORM, p.provider_id)
            if existing:
                continue
            session.add(
                ProviderORM(
                    id=p.provider_id,
                    name=p.name,
                    credentials=p.credentials,
                    services=p.services,
                    location=p.location,
                    teleconsultation_available=p.teleconsultation_available,
                    verified=p.verified,
                    active=True,
                )
            )
        await session.commit()
    print(f"Seeded {len(SIMULATED_PROVIDERS)} simulated providers.")


if __name__ == "__main__":
    asyncio.run(main())
