"""Tests for lux-mon button platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon.button import BUTTON_DESCRIPTIONS, LuxmonButton


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {"soc": {"value": 42.0, "unit": "%"}},
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
async def test_quick_charge_start_button(mock_coordinator, mock_entry):
    mock_coordinator._client.quick_charge_start = AsyncMock(return_value={"ok": True})
    entity = LuxmonButton(mock_coordinator, mock_entry, "quick_charge_start")
    await entity.async_press()
    mock_coordinator._client.quick_charge_start.assert_awaited_once()


@pytest.mark.asyncio
async def test_quick_charge_stop_button(mock_coordinator, mock_entry):
    mock_coordinator._client.quick_charge_stop = AsyncMock(return_value={"ok": True})
    entity = LuxmonButton(mock_coordinator, mock_entry, "quick_charge_stop")
    await entity.async_press()
    mock_coordinator._client.quick_charge_stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_button_press_logs_error(mock_coordinator, mock_entry):
    mock_coordinator._client.quick_charge_start = AsyncMock(side_effect=RuntimeError("boom"))
    entity = LuxmonButton(mock_coordinator, mock_entry, "quick_charge_start")
    with pytest.raises(RuntimeError):
        await entity.async_press()


def test_button_descriptions_complete():
    assert "quick_charge_start" in BUTTON_DESCRIPTIONS
    assert "quick_charge_stop" in BUTTON_DESCRIPTIONS
