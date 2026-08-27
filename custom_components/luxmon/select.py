"""Select platform for lux-mon controllable settings."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
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
    """Set up lux-mon select entities from config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    client = coordinator._client
    session = coordinator._session
    controllable = await client.get_controllable_settings(session)
    settings = controllable.get("settings", {})

    entities: list[LuxmonSelect] = []
    for name, meta in settings.items():
        if meta.get("type") != "select":
            continue
        entities.append(LuxmonSelect(coordinator, entry, name, meta))

    async_add_entities(entities)


class LuxmonSelect(LuxmonEntity, SelectEntity):
    """Representation of a lux-mon select setting."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        name: str,
        meta: dict[str, Any],
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, entry, name)
        self._setting_name = name
        self._meta = meta
        options = meta.get("options") or []
        self._attr_options = [str(opt["value"]) for opt in options]
        self._option_labels = {str(opt["value"]): opt.get("label", opt["value"]) for opt in options}
        self.entity_description = SelectEntityDescription(
            key=name,
            name=meta.get("label", name),
        )
        self._attr_unique_id = f"{entry.entry_id}_{name}_select"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        raw = self._meta.get("value")
        if raw is None:
            return None
        return str(raw)

    async def async_select_option(self, option: str) -> None:
        """Update the setting on lux-mon."""
        await self.coordinator._client.set_setting(
            self.coordinator._session, self._setting_name, option
        )
        self._meta["value"] = option
        self.async_write_ha_state()
