"""Tests for lux-mon select platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon.select import LuxmonSelect


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {"state": {"value": 4, "unit": ""}},
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
def select_meta():
    return {
        "value": "solar_first",
        "type": "select",
        "label": "Output source priority",
        "options": [
            {"value": "solar_first", "label": "Solar first"},
            {"value": "sbu", "label": "SBU"},
            {"value": "utility_first", "label": "Utility first"},
        ],
    }


def test_select_metadata(mock_coordinator, mock_entry, select_meta):
    entity = LuxmonSelect(mock_coordinator, mock_entry, "output_source_priority", select_meta)
    assert entity._attr_unique_id == "test-entry-id_output_source_priority_select"
    assert entity._attr_options == ["solar_first", "sbu", "utility_first"]
    assert entity.current_option == "solar_first"


@pytest.mark.asyncio
async def test_select_option(mock_coordinator, mock_entry, select_meta):
    mock_coordinator._client.set_setting = AsyncMock(return_value={"updated": True})
    entity = LuxmonSelect(mock_coordinator, mock_entry, "output_source_priority", select_meta)
    await entity.async_select_option("sbu")
    mock_coordinator._client.set_setting.assert_awaited_once_with(
        mock_coordinator._session, "output_source_priority", "sbu"
    )
    assert entity._meta["value"] == "sbu"


def test_select_none_value(mock_coordinator, mock_entry, select_meta):
    select_meta["value"] = None
    entity = LuxmonSelect(mock_coordinator, mock_entry, "output_source_priority", select_meta)
    assert entity.current_option is None
