"""Shared pytest fixtures and module stubs."""
import os
import sys
import types
from typing import Generic, TypeVar
from unittest.mock import MagicMock

# Ensure custom_components/luxmon is importable from tests.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))
sys.path.insert(0, ROOT)


_T = TypeVar("_T")


def _make_module(name: str, attrs: dict = None) -> types.ModuleType:
    module = types.ModuleType(name)
    for key, value in (attrs or {}).items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


# Minimal stubs for Home Assistant modules so integration code can be imported
# without the full HA core checkout (which is Python 3.13-incompatible here).
ha = _make_module("homeassistant")
ha_const = _make_module(
    "homeassistant.const",
    {
        "CONF_HOST": "host",
        "CONF_PORT": "port",
        "CONF_SCAN_INTERVAL": "scan_interval",
        "PERCENTAGE": "%",
        "Platform": type("Platform", (), {
            "SENSOR": "sensor",
            "NUMBER": "number",
            "SELECT": "select",
            "SWITCH": "switch",
            "BINARY_SENSOR": "binary_sensor",
            "BUTTON": "button",
        }),
        "UnitOfElectricCurrent": type("UnitOfElectricCurrent", (), {"AMPERE": "A"}),
        "UnitOfElectricPotential": type("UnitOfElectricPotential", (), {"VOLT": "V"}),
        "UnitOfEnergy": type("UnitOfEnergy", (), {"KILO_WATT_HOUR": "kWh"}),
        "UnitOfFrequency": type("UnitOfFrequency", (), {"HERTZ": "Hz"}),
        "UnitOfPower": type("UnitOfPower", (), {"WATT": "W"}),
        "UnitOfTemperature": type("UnitOfTemperature", (), {"CELSIUS": "°C"}),
        "UnitOfTime": type("UnitOfTime", (), {"MINUTES": "min"}),
        "EntityCategory": type("EntityCategory", (), {
            "DIAGNOSTIC": "diagnostic",
            "CONFIG": "config",
        }),
    },
)


class _FakeCoordinator(Generic[_T]):
    pass


class _FakeCoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @classmethod
    def __class_getitem__(cls, item):
        return cls

    def async_write_ha_state(self):
        pass


ha.helpers = _make_module("homeassistant.helpers")
ha.helpers.config_validation = _make_module(
    "homeassistant.helpers.config_validation",
    {"config_entry_only_config_schema": lambda domain: {},
     "empty_config_schema": lambda domain: {},
     "platform_only_config_schema": lambda domain: {}},
)
ha.helpers.aiohttp_client = _make_module(
    "homeassistant.helpers.aiohttp_client",
    {"async_get_clientsession": MagicMock},
)
ha.helpers.device_registry = _make_module(
    "homeassistant.helpers.device_registry",
    {"DeviceInfo": MagicMock},
)
ha.helpers.entity_platform = _make_module(
    "homeassistant.helpers.entity_platform",
    {"AddEntitiesCallback": MagicMock},
)
ha.helpers.update_coordinator = _make_module(
    "homeassistant.helpers.update_coordinator",
    {
        "CoordinatorEntity": _FakeCoordinatorEntity,
        "DataUpdateCoordinator": _FakeCoordinator,
        "UpdateFailed": Exception,
    },
)
ha.config_entries = _make_module(
    "homeassistant.config_entries",
    {"ConfigEntry": MagicMock, "ConfigEntryNotReady": Exception},
)
ha.core = _make_module(
    "homeassistant.core",
    {"HomeAssistant": MagicMock, "callback": lambda fn: fn, "ServiceCall": MagicMock},
)
ha.data_entry_flow = _make_module(
    "homeassistant.data_entry_flow",
    {"FlowResult": MagicMock, "FlowHandler": MagicMock},
)
ha.components = _make_module("homeassistant.components")
ha.components.binary_sensor = _make_module(
    "homeassistant.components.binary_sensor",
    {
        "BinarySensorDeviceClass": type("BinarySensorDeviceClass", (), {"PROBLEM": "problem"}),
        "BinarySensorEntity": object,
        "BinarySensorEntityDescription": MagicMock,
    },
)
ha.components.button = _make_module(
    "homeassistant.components.button",
    {"ButtonEntity": object, "ButtonEntityDescription": MagicMock},
)
ha.components.number = _make_module(
    "homeassistant.components.number",
    {"NumberEntity": object, "NumberEntityDescription": MagicMock, "NumberMode": type("NumberMode", (), {"AUTO": "auto", "BOX": "box", "SLIDER": "slider"})},
)
ha.components.select = _make_module(
    "homeassistant.components.select",
    {"SelectEntity": object, "SelectEntityDescription": MagicMock},
)
ha.components.sensor = _make_module(
    "homeassistant.components.sensor",
    {
        "SensorDeviceClass": type("SensorDeviceClass", (), {
            "BATTERY": "battery",
            "CURRENT": "current",
            "ENERGY": "energy",
            "FREQUENCY": "frequency",
            "POWER": "power",
            "TEMPERATURE": "temperature",
            "VOLTAGE": "voltage",
        }),
        "SensorEntity": object,
        "SensorEntityDescription": MagicMock,
        "SensorStateClass": type("SensorStateClass", (), {
            "MEASUREMENT": "measurement",
            "TOTAL_INCREASING": "total_increasing",
        }),
    },
)
ha.components.switch = _make_module(
    "homeassistant.components.switch",
    {"SwitchEntity": object, "SwitchEntityDescription": MagicMock},
)
