"""Constants for the lux-mon integration."""
from __future__ import annotations

from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
import homeassistant.helpers.config_validation as cv

DOMAIN = "luxmon"

# This integration is config-entry only (no YAML configuration).
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

DEFAULT_HOST = "192.168.1.100"
DEFAULT_PORT = 8080
DEFAULT_SCAN_INTERVAL = 30

CONF_DEVICE_ID = "device_id"
CONF_INVERTER_MODEL = "inverter_model"

# Entity categories
CATEGORY_CONTROL = "control"
CATEGORY_CONFIG = "config"
CATEGORY_DIAGNOSTIC = "diagnostic"

# Static metadata map for common lux-mon registers.
# Keys match the names emitted by lux-mon /api/status.
# Where device_class/state_class are None, the platform falls back to plain sensor.
SENSOR_METADATA: dict[str, dict] = {
    "soc": {
        "name": "Battery SOC",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": PERCENTAGE,
    },
    "soh": {
        "name": "Battery SOH",
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": PERCENTAGE,
    },
    "battery_voltage": {
        "name": "Battery voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfElectricPotential.VOLT,
    },
    "battery_current": {
        "name": "Battery current",
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfElectricCurrent.AMPERE,
    },
    "pv1_voltage": {
        "name": "PV1 voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfElectricPotential.VOLT,
    },
    "pv2_voltage": {
        "name": "PV2 voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfElectricPotential.VOLT,
    },
    "pv3_voltage": {
        "name": "PV3 voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfElectricPotential.VOLT,
    },
    "pv1_power": {
        "name": "PV1 power",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "pv2_power": {
        "name": "PV2 power",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "pv3_power": {
        "name": "PV3 power",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "pv_power_total": {
        "name": "PV power total",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "pv_energy_total": {
        "name": "PV energy total",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
    },
    "grid_import_power": {
        "name": "Grid import power",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "grid_export_power": {
        "name": "Grid export power",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "grid_import_energy_total": {
        "name": "Grid import energy total",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
    },
    "grid_export_energy_total": {
        "name": "Grid export energy total",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
    },
    "battery_in_energy_total": {
        "name": "Battery charge energy total",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
    },
    "battery_out_energy_total": {
        "name": "Battery discharge energy total",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
    },
    "eps_power": {
        "name": "EPS power",
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfPower.WATT,
    },
    "grid_voltage_r": {
        "name": "Grid voltage R",
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfElectricPotential.VOLT,
    },
    "grid_frequency": {
        "name": "Grid frequency",
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfFrequency.HERTZ,
    },
    "temp_inverter": {
        "name": "Inverter temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
    },
    "temp_radiator_1": {
        "name": "Radiator 1 temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
        "entity_registry_enabled_default": False,
    },
    "temp_radiator_2": {
        "name": "Radiator 2 temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
        "entity_registry_enabled_default": False,
    },
    "temp_battery": {
        "name": "Battery temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
    },
    "fault": {
        "name": "Fault code",
        "entity_registry_enabled_default": False,
    },
}
