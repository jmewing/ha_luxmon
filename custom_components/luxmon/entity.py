"""Base entity for lux-mon."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LuxmonDataUpdateCoordinator


class LuxmonEntity(CoordinatorEntity[LuxmonDataUpdateCoordinator]):
    """Base entity for all lux-mon entities."""

    def __init__(
        self,
        coordinator: LuxmonDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._key = key
        self._entry = entry

        host = entry.data[CONF_HOST]
        device_id = entry.options.get("device_id") or entry.data.get("device_id") or f"luxmon_{host.replace('.', '_')}"
        device_name = entry.options.get("device_name") or entry.data.get("device_name") or f"lux-mon {host}"

        self._attr_unique_id = f"{entry.entry_id}_{device_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{device_id}")},
            name=device_name,
            manufacturer="lux-mon",
            model=entry.options.get("inverter_model") or entry.data.get("inverter_model") or "lux-mon inverter",
        )

    @property
    def _holding(self) -> dict:
        """Return the latest holding-register dict from the coordinator."""
        data = self.coordinator.data or {}
        return data.get("holding", {})

    @property
    def _holding_value(self) -> float | int | None:
        """Return the current raw/scaled value for this entity's key."""
        item = self._holding.get(self._key)
        if not isinstance(item, dict):
            return None
        raw = item.get("raw")
        if raw is None:
            return None
        scale = item.get("scale", 1.0) or 1.0
        val = raw * scale
        # Return int when scale is 1.0 and value is integral, else float.
        if scale == 1.0 and isinstance(val, float) and val.is_integer():
            return int(val)
        return val

    @property
    def _snapshot(self) -> dict:
        """Return the latest lux-mon snapshot dict."""
        data = self.coordinator.data or {}
        return data.get("registers", {})

    def _value(self) -> float | int | str | None:
        """Extract the numeric/string value for this entity's key."""
        item = self._snapshot.get(self._key)
        if isinstance(item, dict):
            return item.get("value")
        return item

    @property
    def _unit_of_measurement(self) -> str | None:
        """Return the unit of measurement from lux-mon if available.

        Returns None for empty-string units so HA does not treat the entity
        as numeric (an empty string unit would otherwise trigger HA's
        numeric-coercion path and raise on string values).
        """
        item = self._snapshot.get(self._key)
        if isinstance(item, dict):
            unit = item.get("unit")
            return unit or None
        return None
