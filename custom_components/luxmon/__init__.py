"""The lux-mon integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant, callback, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LuxMonApiClient
from .const import DOMAIN
from .coordinator import LuxmonDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SELECT, Platform.SWITCH, Platform.BINARY_SENSOR, Platform.BUTTON]

SERVICE_QUICK_CHARGE_START = "quick_charge_start"
SERVICE_QUICK_CHARGE_STOP = "quick_charge_stop"
SERVICE_SET_SETTING = "set_setting"
SERVICE_LOAD_AUTOMATION_RULES = "load_automation_rules"

SCHEMA_QUICK_CHARGE_START = vol.Schema(
    {
        vol.Optional("amps"): vol.Coerce(int),
        vol.Optional("minutes"): vol.Coerce(int),
    },
    extra=vol.ALLOW_EXTRA,
)
SCHEMA_QUICK_CHARGE_STOP = vol.Schema({})
SCHEMA_SET_SETTING = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("value"): vol.Any(str, int, float, bool),
    }
)
SCHEMA_LOAD_AUTOMATION_RULES = vol.Schema(
    {
        vol.Required("rules"): list,
        vol.Optional("enabled", default=True): bool,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up global lux-mon services."""

    async def _handle_quick_charge_start(call: ServiceCall) -> None:
        amps = call.data.get("amps")
        minutes = call.data.get("minutes")
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator._client.quick_charge_start(
                coordinator._session, amps=amps, minutes=minutes
            )
            break  # service targets first configured instance

    async def _handle_quick_charge_stop(call: ServiceCall) -> None:
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator._client.quick_charge_stop(coordinator._session)
            break

    async def _handle_set_setting(call: ServiceCall) -> None:
        name = call.data["name"]
        value = call.data["value"]
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator._client.set_setting(
                coordinator._session, name, value
            )
            break

    async def _handle_load_automation_rules(call: ServiceCall) -> None:
        rules = call.data["rules"]
        enabled = call.data.get("enabled", True)
        for coordinator in hass.data.get(DOMAIN, {}).values():
            await coordinator._client.load_automation_rules(
                coordinator._session, rules, enabled=enabled
            )
            break

    hass.services.async_register(
        DOMAIN, SERVICE_QUICK_CHARGE_START, _handle_quick_charge_start, schema=SCHEMA_QUICK_CHARGE_START
    )
    hass.services.async_register(
        DOMAIN, SERVICE_QUICK_CHARGE_STOP, _handle_quick_charge_stop, schema=SCHEMA_QUICK_CHARGE_STOP
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_SETTING, _handle_set_setting, schema=SCHEMA_SET_SETTING
    )
    hass.services.async_register(
        DOMAIN, SERVICE_LOAD_AUTOMATION_RULES, _handle_load_automation_rules, schema=SCHEMA_LOAD_AUTOMATION_RULES
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lux-mon from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    token = entry.data.get("api_token")

    client = LuxMonApiClient(host, port, token)
    session = async_get_clientsession(hass)

    # Verify connectivity early.
    healthy = await client.get_health(session)
    if not healthy:
        _LOGGER.error(" lux-mon API at %s:%d is not reachable", host, port)
        raise ConfigEntryNotReady(f" lux-mon API at {host}:{port} is not reachable")

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, 30))

    coordinator = LuxmonDataUpdateCoordinator(hass, session, client, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator: LuxmonDataUpdateCoordinator = hass.data[DOMAIN].get(entry.entry_id)
    diagnostics: dict = {
        "entry": {
            "title": entry.title,
            "host": entry.data.get(CONF_HOST),
            "port": entry.data.get(CONF_PORT),
            "scan_interval": entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, 30)),
        },
        "data_last_update_success": coordinator.last_update_success if coordinator else None,
    }
    if coordinator and coordinator.data:
        diagnostics["snapshot_id"] = coordinator.data.get("snapshot_id")
        diagnostics["timestamp"] = coordinator.data.get("timestamp")
        registers = coordinator.data.get("registers", {})
        diagnostics["register_count"] = len(registers)
        diagnostics["register_keys"] = sorted(registers.keys())[:50]
    return diagnostics
