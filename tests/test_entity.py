"""Unit tests for lux-mon entity base class."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.luxmon.const import DOMAIN
from custom_components.luxmon.entity import LuxmonEntity


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {
        "snapshot_id": 1,
        "timestamp": "2026-08-27T10:00:00-05:00",
        "registers": {
            "soc": {"value": 42.0, "unit": "%"},
            "battery_voltage": {"value": 51.2, "unit": "V"},
        },
    }
    return coordinator


@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.data = {"host": "192.168.1.100", "port": 8080}
    entry.options = {"device_id": "testdevice", "inverter_model": "EG4 6000XP"}
    entry.entry_id = "test-entry-id"
    return entry


def test_entity_value(mock_coordinator, mock_entry):
    entity = LuxmonEntity(mock_coordinator, mock_entry, "soc")
    assert entity._value() == 42.0


def test_entity_unit(mock_coordinator, mock_entry):
    entity = LuxmonEntity(mock_coordinator, mock_entry, "soc")
    assert entity._unit_of_measurement == "%"


def test_entity_device_info(mock_coordinator, mock_entry):
    entity = LuxmonEntity(mock_coordinator, mock_entry, "soc")
    info = entity._attr_device_info
    assert info.manufacturer == "lux-mon"
    assert info.model == "EG4 6000XP"
    assert (DOMAIN, "test-entry-id_testdevice") in info.identifiers
