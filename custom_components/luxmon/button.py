"""Button platform for lux-mon quick charge actions."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxmonDataUpdateCoordinator
from .entity import LuxmonEntity

_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTIONS = {
    "quick_charge_start": ButtonEntityDescription(
        key="quick_charge_start",
        name="Quick charge start",
        icon="mdi:lightning-bolt",
    ),
    "quick_charge_stop": ButtonEntityDescription(
        key="quick_charge_stop",
        name="Quick charge stop",
        icon="mdi:lightning-bolt-off",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lux-mon button entities from config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        LuxmonButton(coordinator, entry, key)
        for key in BUTTON_DESCRIPTIONS
    ]
    async_add_entities(entities)


class LuxmonButton(LuxmonEntity, ButtonEntity):
    """Representation of a lux-mon button."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry, key)
        self.entity_description = BUTTON_DESCRIPTIONS[key]
        self._attr_unique_id = f"{entry.entry_id}_{key}_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        client = self.coordinator._client
        session = self.coordinator._session
        try:
            if self.entity_description.key == "quick_charge_start":
                await client.quick_charge_start(session)
            elif self.entity_description.key == "quick_charge_stop":
                await client.quick_charge_stop(session)
        except Exception as exc:
            _LOGGER.error("lux-mon button %s failed: %s", self.entity_description.key, exc)
            raise
