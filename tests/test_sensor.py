"""Unit tests for lux-mon sensor platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.luxmon.const import DOMAIN


@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {DOMAIN: {"test-entry-id": MagicMock()}}
    return hass


@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.entry_id = "test-entry-id"
    return entry


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {
            "soc": {"value": 42.0, "unit": "%"},
            "pv_energy_total": {"value": 1234.5, "unit": "kWh"},
        },
    }
    return coordinator


@pytest.mark.asyncio
async def test_async_setup_entry(mock_hass, mock_entry, mock_coordinator):
    mock_hass.data[DOMAIN][mock_entry.entry_id] = mock_coordinator
    added = []

    from custom_components.luxmon import sensor

    await sensor.async_setup_entry(mock_hass, mock_entry, added.extend)

    assert len(added) == 2
    assert any(e._key == "soc" for e in added)
    assert any(e._key == "pv_energy_total" for e in added)
