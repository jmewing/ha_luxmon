"""Tests for lux-mon binary_sensor platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon.binary_sensor import ALERT_DESCRIPTIONS, LuxmonBinarySensor


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {"soc": {"value": 15.0, "unit": "%"}},
    }
    return coordinator


@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.data = {"host": "192.168.1.100", "port": 8080}
    entry.options = {"device_id": "testdevice", "inverter_model": "EG4 6000XP"}
    entry.entry_id = "test-entry-id"
    return entry


@pytest.mark.asyncio
async def test_binary_sensor_active(mock_coordinator, mock_entry):
    mock_coordinator._client.get_alerts = AsyncMock(
        return_value={"alerts": {"battery_soc_low": {"active": True, "value": 15.0, "message": "Low"}}}
    )
    entity = LuxmonBinarySensor(mock_coordinator, mock_entry, "battery_soc_low")
    await entity._async_update_alerts()
    assert entity.is_on is True


@pytest.mark.asyncio
async def test_binary_sensor_inactive(mock_coordinator, mock_entry):
    mock_coordinator._client.get_alerts = AsyncMock(
        return_value={"alerts": {"battery_soc_low": {"active": False, "value": 50.0, "message": "OK"}}}
    )
    entity = LuxmonBinarySensor(mock_coordinator, mock_entry, "battery_soc_low")
    await entity._async_update_alerts()
    assert entity.is_on is False


@pytest.mark.asyncio
async def test_binary_sensor_api_failure(mock_coordinator, mock_entry):
    mock_coordinator._alerts_data = {}
    mock_coordinator._client.get_alerts = AsyncMock(side_effect=RuntimeError("API down"))
    entity = LuxmonBinarySensor(mock_coordinator, mock_entry, "battery_soc_low")
    await entity._async_update_alerts()
    assert entity.is_on is None


def test_alert_descriptions_complete():
    assert "battery_soc_low" in ALERT_DESCRIPTIONS
    assert "grid_loss" in ALERT_DESCRIPTIONS
    for desc in ALERT_DESCRIPTIONS.values():
        assert desc.device_class is not None
