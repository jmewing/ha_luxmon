"""Tests for lux-mon diagnostics."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.luxmon import async_get_config_entry_diagnostics


@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.title = "lux-mon (192.168.1.100:8080)"
    entry.entry_id = "test-entry-id"
    entry.data = {"host": "192.168.1.100", "port": 8080}
    entry.options = {"scan_interval": 30}
    return entry


@pytest.fixture
def mock_hass():
    return MagicMock()


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.data = {
        "snapshot_id": 42,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {
            "soc": {"value": 42.0, "unit": "%"},
            "battery_voltage": {"value": 51.2, "unit": "V"},
        },
    }
    return coordinator


@pytest.mark.asyncio
async def test_diagnostics_redacts_token(mock_hass, mock_entry, mock_coordinator):
    mock_hass.data = {"luxmon": {"test-entry-id": mock_coordinator}}
    diag = await async_get_config_entry_diagnostics(mock_hass, mock_entry)
    assert diag["entry"]["host"] == "192.168.1.100"
    assert diag["entry"]["port"] == 8080
    assert diag["entry"]["scan_interval"] == 30
    assert diag["data_last_update_success"] is True
    assert diag["snapshot_id"] == 42
    assert diag["register_count"] == 2
    assert "soc" in diag["register_keys"]
    # Token is not present because it was never set on this fixture
    assert "api_token" not in diag["entry"]


@pytest.mark.asyncio
async def test_diagnostics_no_coordinator(mock_hass, mock_entry):
    mock_hass.data = {"luxmon": {}}
    diag = await async_get_config_entry_diagnostics(mock_hass, mock_entry)
    assert diag["data_last_update_success"] is None
    assert "snapshot_id" not in diag
