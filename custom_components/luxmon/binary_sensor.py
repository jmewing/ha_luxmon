"""Binary sensor platform for lux-mon live alert states."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxmonDataUpdateCoordinator
from .entity import LuxmonEntity

_LOGGER = logging.getLogger(__name__)

ALERT_DESCRIPTIONS: dict[str, BinarySensorEntityDescription] = {
    "battery_soc_low": BinarySensorEntityDescription(
        key="battery_soc_low",
        name="Battery SOC low",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    "battery_soc_critical": BinarySensorEntityDescription(
        key="battery_soc_critical",
        name="Battery SOC critical",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    "battery_temp_high": BinarySensorEntityDescription(
        key="battery_temp_high",
        name="Battery temperature high",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    "inverter_temp_high": BinarySensorEntityDescription(
        key="inverter_temp_high",
        name="Inverter temperature high",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    "grid_loss": BinarySensorEntityDescription(
        key="grid_loss",
        name="Grid loss",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    "fault_active": BinarySensorEntityDescription(
        key="fault_active",
        name="Fault active",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lux-mon binary sensor entities from config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        LuxmonBinarySensor(coordinator, entry, key)
        for key in ALERT_DESCRIPTIONS
    ]
    async_add_entities(entities)


class LuxmonBinarySensor(LuxmonEntity, BinarySensorEntity):
    """Representation of a lux-mon alert binary sensor."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry, key)
        self.entity_description = ALERT_DESCRIPTIONS[key]
        self._attr_unique_id = f"{entry.entry_id}_{key}_binary_sensor"
        self._alert_key = key

    @property
    def is_on(self) -> bool | None:
        """Return True if the alert is active."""
        data = getattr(self.coordinator, "_alerts_data", {})
        return data.get(self._alert_key, {}).get("active")

    async def async_added_to_hass(self) -> None:
        """Fetch alert state when entity is added."""
        await super().async_added_to_hass()
        await self._async_update_alerts()

    async def _async_update_alerts(self) -> None:
        """Refresh the live alert states from the API."""
        try:
            result = await self.coordinator._client.get_alerts(self.coordinator._session)
            self.coordinator._alerts_data = result.get("alerts", {})
            self.async_write_ha_state()
        except Exception:
            _LOGGER.debug("Failed to fetch live alert states")

    async def async_update(self) -> None:
        """Update the entity."""
        await self._async_update_alerts()
