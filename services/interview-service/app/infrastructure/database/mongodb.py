"""MongoDB connection lifecycle management (Motor async client)."""
from __future__ import annotations

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import Settings

logger = logging.getLogger(__name__)


class MongoDB:
    """Holds the Motor client/database and manages connection lifecycle.

    A single instance is created at application startup and shared across
    repositories via dependency injection, keeping infrastructure concerns
    out of the domain/application layers.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self.client: AsyncIOMotorClient | None = None
        self.database: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        logger.info("Connecting to MongoDB at %s", self._mask_url(self._settings.MONGODB_URL))
        # tz_aware=True is important: without it, PyMongo/Motor deserialize
        # BSON dates as naive UTC datetimes, which breaks arithmetic against
        # the timezone-aware `datetime.now(timezone.utc)` values used
        # throughout the domain/application layers (e.g. remaining_seconds).
        self.client = AsyncIOMotorClient(self._settings.MONGODB_URL, tz_aware=True)
        self.database = self.client[self._settings.MONGODB_DATABASE]
        await self._ensure_indexes()

    async def disconnect(self) -> None:
        if self.client is not None:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.database = None

    async def ping(self) -> bool:
        """Used by /ready to verify DB connectivity. Never raises."""
        if self.client is None:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:  # noqa: BLE001 - readiness probe must not raise
            logger.exception("MongoDB readiness ping failed")
            return False

    async def _ensure_indexes(self) -> None:
        if self.database is None:
            return
        try:
            await self.database["interviews"].create_index("user_id")
            await self.database["interviews"].create_index("status")
            await self.database["questions"].create_index("status")
            await self.database["questions"].create_index("category")
            await self.database["questions"].create_index("tags")
        except Exception:  # noqa: BLE001 - index creation must not block startup
            logger.exception("Failed to ensure MongoDB indexes")

    @staticmethod
    def _mask_url(url: str) -> str:
        """Avoid leaking credentials embedded in the connection string in logs."""
        if "@" in url:
            scheme_and_creds, rest = url.rsplit("@", 1)
            scheme = scheme_and_creds.split("//")[0]
            return f"{scheme}//***:***@{rest}"
        return url
