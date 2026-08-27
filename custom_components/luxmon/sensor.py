"""Sensor platform for lux-mon."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_METADATA
from .coordinator import LuxmonDataUpdateCoordinator
from .entity import LuxmonEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lux-mon sensors from config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    snapshot = data.get("registers", {})

    entities: list[LuxmonSensor] = []
    for key in snapshot:
        if not isinstance(snapshot[key], dict):
            continue
        entities.append(LuxmonSensor(coordinator, entry, key))

    async_add_entities(entities)


class LuxmonSensor(LuxmonEntity, SensorEntity):
    """Representation of a lux-mon sensor."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, key)
        meta = SENSOR_METADATA.get(key, {})

        self._attr_name = meta.get("name", key.replace("_", " ").title())
        self._attr_device_class = meta.get("device_class")
        self._attr_state_class = meta.get("state_class")
        # Only set a unit for numeric sensors. String-valued registers (e.g.
        # state_label) must have native_unit_of_measurement = None so HA does
        # not attempt numeric coercion and raise on the string value.
        unit = meta.get("unit") or self._unit_of_measurement
        self._attr_native_unit_of_measurement = unit or None
        self._attr_entity_registry_enabled_default = meta.get(
            "entity_registry_enabled_default", True
        )
        if meta.get("diagnostic"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        return self._value()
