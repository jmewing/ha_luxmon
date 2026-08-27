"""Switch platform for lux-mon controllable settings."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
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
    """Set up lux-mon switch entities from config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    client = coordinator._client
    session = coordinator._session
    controllable = await client.get_controllable_settings(session)
    settings = controllable.get("settings", {})

    entities: list[LuxmonSwitch] = []
    for name, meta in settings.items():
        if meta.get("type") not in ("checkbox", "boolean"):
            continue
        entities.append(LuxmonSwitch(coordinator, entry, name, meta))

    async_add_entities(entities)


class LuxmonSwitch(LuxmonEntity, SwitchEntity):
    """Representation of a lux-mon switch setting."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        meta: dict[str, Any],
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, entry, name)
        self._setting_name = name
        self._meta = meta
        self.entity_description = SwitchEntityDescription(
            key=name,
            name=meta.get("label", name),
        )
        self._attr_unique_id = f"{entry.entry_id}_{name}_switch"

    @property
    def is_on(self) -> bool | None:
        """Return True if the setting is enabled."""
        raw = self._meta.get("value")
        if raw is None:
            return None
        return str(raw).lower() in ("true", "1", "yes", "on")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the setting on."""
        await self.coordinator._client.set_setting(
            self.coordinator._session, self._setting_name, "true"
        )
        self._meta["value"] = "true"
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the setting off."""
        await self.coordinator._client.set_setting(
            self.coordinator._session, self._setting_name, "false"
        )
        self._meta["value"] = "false"
        self.async_write_ha_state()
