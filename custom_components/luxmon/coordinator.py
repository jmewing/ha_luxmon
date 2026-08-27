"""DataUpdateCoordinator for lux-mon."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LuxMonApiClient

_LOGGER = logging.getLogger(__name__)


class LuxmonDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll lux-mon /api/status and provide the latest snapshot to platforms."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        client: LuxMonApiClient,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self._session = session
        self._client = client

        super().__init__(
            hass,
            _LOGGER,
            name="luxmon",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from lux-mon."""
        try:
            data = await self._client.get_status(self._session)
        except Exception as exc:
            raise UpdateFailed(f"Error fetching lux-mon data: {exc}") from exc

        return data
