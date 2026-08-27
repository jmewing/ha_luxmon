"""Tests for lux-mon switch platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon.switch import LuxmonSwitch


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {"grid_charge_enable": {"value": 1, "unit": ""}},
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
def switch_meta():
    return {
        "value": "true",
        "type": "checkbox",
        "label": "Grid charge enable",
    }


def test_switch_on(mock_coordinator, mock_entry, switch_meta):
    entity = LuxmonSwitch(mock_coordinator, mock_entry, "grid_charge_enable", switch_meta)
    assert entity.is_on is True
    assert entity._attr_unique_id == "test-entry-id_grid_charge_enable_switch"


@pytest.mark.asyncio
async def test_switch_turn_on(mock_coordinator, mock_entry, switch_meta):
    mock_coordinator._client.set_setting = AsyncMock(return_value={"updated": True})
    entity = LuxmonSwitch(mock_coordinator, mock_entry, "grid_charge_enable", switch_meta)
    await entity.async_turn_on()
    mock_coordinator._client.set_setting.assert_awaited_once_with(
        mock_coordinator._session, "grid_charge_enable", "true"
    )
    assert entity._meta["value"] == "true"


@pytest.mark.asyncio
async def test_switch_turn_off(mock_coordinator, mock_entry, switch_meta):
    mock_coordinator._client.set_setting = AsyncMock(return_value={"updated": True})
    entity = LuxmonSwitch(mock_coordinator, mock_entry, "grid_charge_enable", switch_meta)
    await entity.async_turn_off()
    mock_coordinator._client.set_setting.assert_awaited_once_with(
        mock_coordinator._session, "grid_charge_enable", "false"
    )
    assert entity._meta["value"] == "false"


def test_switch_variants(mock_coordinator, mock_entry, switch_meta):
    for raw, expected in [("1", True), ("yes", True), ("on", True), ("false", False), ("0", False)]:
        switch_meta["value"] = raw
        entity = LuxmonSwitch(mock_coordinator, mock_entry, "grid_charge_enable", switch_meta)
        assert entity.is_on is expected
