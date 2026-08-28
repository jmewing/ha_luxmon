"""Number platform for lux-mon controllable settings."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxmonDataUpdateCoordinator
from .entity import LuxmonEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lux-mon number entities from config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    client = coordinator._client
    session = coordinator._session
    controllable = await client.get_controllable_settings(session)
    settings = controllable.get("settings", {})

    entities: list[LuxmonNumber] = []
    for name, meta in settings.items():
        if meta.get("type") != "number":
            continue
        entities.append(LuxmonNumber(coordinator, entry, name, meta))

    async_add_entities(entities)


class LuxmonNumber(LuxmonEntity, NumberEntity):
    """Representation of a lux-mon number setting."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        meta: dict[str, Any],
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, entry, name)
        self._setting_name = name
        self._meta = meta
        self.entity_description = NumberEntityDescription(
            key=name,
            name=meta.get("label", name),
            native_unit_of_measurement=meta.get("unit") or None,
        )
        self._attr_native_min_value = meta.get("min")
        self._attr_native_max_value = meta.get("max")
        self._attr_native_step = meta.get("step")
        self._attr_mode = NumberMode.AUTO
        self._attr_unique_id = f"{entry.entry_id}_{name}_number"

    @property
    def native_value(self) -> float | int | None:
        """Return the current value from live holding-register reads."""
        return self._holding_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the holding register on lux-mon."""
        step = self._attr_native_step
        if step is not None and step == int(step):
            value = int(value)
        await self.coordinator._client.set_holding(
            self.coordinator._session, self._setting_name, value
        )
        self._meta["value"] = value
        self.async_write_ha_state()
