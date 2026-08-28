"""Async client for the lux-mon REST API."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class LuxMonApiClient:
    """Thin async client for lux-mon's FastAPI server."""

    def __init__(self, host: str, port: int, token: str | None = None):
        self._host = host
        self._port = port
        self._token = token
        self._base_url = f"http://{host}:{port}"

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def get_health(self, session: aiohttp.ClientSession) -> bool:
        """Return True if /api/health responds with HTTP 200."""
        try:
            async with session.get(
                f"{self._base_url}/api/health",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                return resp.status == 200
        except Exception as exc:
            _LOGGER.debug("Health check failed: %s", exc)
            return False

    async def get_status(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Fetch the latest full decoded snapshot."""
        async with session.get(
            f"{self._base_url}/api/status",
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_summary(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Fetch compact summary metrics."""
        async with session.get(
            f"{self._base_url}/api/summary",
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_settings(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Fetch all runtime settings."""
        async with session.get(
            f"{self._base_url}/api/settings",
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def set_setting(
        self, session: aiohttp.ClientSession, name: str, value: Any
    ) -> dict[str, Any]:
        """Update a single runtime setting."""
        async with session.put(
            f"{self._base_url}/api/settings/{name}",
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"value": value},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_alerts(
        self, session: aiohttp.ClientSession
    ) -> dict[str, Any]:
        """Fetch current live alert boolean states."""
        async with session.get(
            f"{self._base_url}/api/alerts/live",
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_controllable_settings(
        self, session: aiohttp.ClientSession
    ) -> dict[str, Any]:
        """Fetch controllable settings metadata.

        Prefers the new /api/holding/controllable endpoint (actual inverter
        holding registers). Falls back to /api/settings/controllable for
        older lux-mon versions.
        """
        try:
            async with session.get(
                f"{self._base_url}/api/holding/controllable",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as exc:
            _LOGGER.debug("Holding controllable endpoint not available: %s", exc)

        try:
            async with session.get(
                f"{self._base_url}/api/settings/controllable",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}
        except Exception as exc:
            _LOGGER.debug("Controllable settings endpoint not available: %s", exc)
            return {}

    async def get_holding(
        self, session: aiohttp.ClientSession
    ) -> dict[str, Any]:
        """Fetch current holding register values directly from the inverter."""
        async with session.get(
            f"{self._base_url}/api/holding",
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def set_holding(
        self, session: aiohttp.ClientSession, name: str, value: Any
    ) -> dict[str, Any]:
        """Write a single named holding register to the inverter."""
        async with session.put(
            f"{self._base_url}/api/holding/{name}",
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"value": value},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def load_automation_rules(
        self,
        session: aiohttp.ClientSession,
        rules: list[dict[str, Any]],
        enabled: bool = True,
    ) -> dict[str, Any]:
        """Replace the full automation rule set and optionally enable the engine."""
        async with session.post(
            f"{self._base_url}/api/automation/rules",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=rules,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
        async with session.post(
            f"{self._base_url}/api/automation/enable",
            headers=self._headers(),
            params={"enabled": "true" if enabled else "false"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def quick_charge_start(
        self,
        session: aiohttp.ClientSession,
        amps: int | None = None,
        minutes: int | None = None,
    ) -> dict[str, Any]:
        """Start a timed quick charge."""
        body: dict[str, Any] = {}
        if amps is not None:
            body["amps"] = amps
        if minutes is not None:
            body["minutes"] = minutes
        async with session.post(
            f"{self._base_url}/api/quick-charge/start",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=body,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def quick_charge_stop(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Stop an active quick charge."""
        async with session.post(
            f"{self._base_url}/api/quick-charge/stop",
            headers=self._headers(),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
