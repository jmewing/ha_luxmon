"""Tests for lux-mon number platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon.number import LuxmonNumber


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {"ac_charge_battery_current": {"value": 10.0, "unit": "A"}},
    }
    return coordinator


@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.data = {"host": "192.168.1.100", "port": 8080}
    entry.options = {"device_id": "testdevice", "inverter_model": "EG4 6000XP"}
    entry.entry_id = "test-entry-id"
    return entry


@pytest.fixture
def number_meta():
    return {
        "value": "15",
        "type": "number",
        "label": "AC charge battery current",
        "min": 0,
        "max": 185,
        "step": 1,
        "unit": "A",
    }


def test_number_metadata(mock_coordinator, mock_entry, number_meta):
    entity = LuxmonNumber(mock_coordinator, mock_entry, "ac_charge_battery_current", number_meta)
    assert entity._attr_unique_id == "test-entry-id_ac_charge_battery_current_number"
    assert entity._attr_native_min_value == 0
    assert entity._attr_native_max_value == 185
    assert entity._attr_native_step == 1
    assert entity.native_value == 15.0


@pytest.mark.asyncio
async def test_number_set_value_int_step(mock_coordinator, mock_entry, number_meta):
    mock_coordinator._client.set_setting = AsyncMock(return_value={"updated": True})
    entity = LuxmonNumber(mock_coordinator, mock_entry, "ac_charge_battery_current", number_meta)
    await entity.async_set_native_value(20)
    mock_coordinator._client.set_setting.assert_awaited_once_with(
        mock_coordinator._session, "ac_charge_battery_current", 20
    )
    assert entity._meta["value"] == 20


@pytest.mark.asyncio
async def test_number_set_value_float_step(mock_coordinator, mock_entry, number_meta):
    number_meta["step"] = 0.5
    mock_coordinator._client.set_setting = AsyncMock(return_value={"updated": True})
    entity = LuxmonNumber(mock_coordinator, mock_entry, "ac_charge_battery_current", number_meta)
    await entity.async_set_native_value(20.5)
    mock_coordinator._client.set_setting.assert_awaited_once_with(
        mock_coordinator._session, "ac_charge_battery_current", 20.5
    )


def test_number_none_value(mock_coordinator, mock_entry, number_meta):
    number_meta["value"] = None
    entity = LuxmonNumber(mock_coordinator, mock_entry, "ac_charge_battery_current", number_meta)
    assert entity.native_value is None
