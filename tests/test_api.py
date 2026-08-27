"""Unit tests for the lux-mon API client."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon.api import LuxMonApiClient


@pytest.fixture
def client():
    return LuxMonApiClient("192.168.1.100", 8080)


class _AsyncContextManager:
    """Helper that wraps a response object as an async context manager."""

    def __init__(self, resp):
        self._resp = resp

    async def __aenter__(self):
        return self._resp

    async def __aexit__(self, *args):
        return False


def _make_response(status: int = 200, json_data=None):
    resp = MagicMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data)
    resp.raise_for_status = MagicMock()
    return resp


def _session_with_get(resp):
    session = MagicMock()
    session.get = MagicMock(return_value=_AsyncContextManager(resp))
    return session


def _session_with_put(resp):
    session = MagicMock()
    session.put = MagicMock(return_value=_AsyncContextManager(resp))
    return session


@pytest.mark.asyncio
async def test_get_health_success(client):
    resp = _make_response(200)
    session = _session_with_get(resp)
    assert await client.get_health(session) is True


@pytest.mark.asyncio
async def test_get_status(client):
    resp = _make_response(
        json_data={
            "snapshot_id": 1,
            "timestamp": "2026-08-27T10:00:00-05:00",
            "registers": {
                "soc": {"value": 42.0, "unit": "%"},
                "battery_voltage": {"value": 51.2, "unit": "V"},
            },
        }
    )
    session = _session_with_get(resp)

    data = await client.get_status(session)
    assert data["registers"]["soc"]["value"] == 42.0


@pytest.mark.asyncio
async def test_set_setting(client):
    resp = _make_response(
        json_data={"name": "alerts_soc_low", "value": "15", "updated": True}
    )
    session = _session_with_put(resp)

    result = await client.set_setting(session, "alerts_soc_low", "15")
    assert result["updated"] is True
