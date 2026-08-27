"""Config flow for lux-mon integration."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN, CONF_DEVICE_ID, CONF_INVERTER_MODEL
from .api import LuxMonApiClient

_LOGGER = logging.getLogger(__name__)

# File written by the HAOS add-on (run.sh) to seed connection defaults.
_ADDON_DEFAULTS_FILE = Path(__file__).parent / ".addon-defaults.json"


def _load_addon_defaults() -> dict[str, Any]:
    """Read add-on-provided connection defaults, if present."""
    try:
        if _ADDON_DEFAULTS_FILE.exists():
            return json.loads(_ADDON_DEFAULTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _LOGGER.debug("Could not read add-on defaults file", exc_info=True)
    return {}


class LuxmonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for lux-mon."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        addon_defaults = _load_addon_defaults()

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input[CONF_PORT])
            client = LuxMonApiClient(host, port)

            try:
                async with aiohttp.ClientSession() as session:
                    healthy = await client.get_health(session)
                if not healthy:
                    errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception(" lux-mon health check failed")
                errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"lux-mon ({host}:{port})",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=addon_defaults.get("host") or DEFAULT_HOST,
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=addon_defaults.get("port") or DEFAULT_PORT,
                ): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                vol.Optional(
                    "api_token",
                    default=addon_defaults.get("api_token") or "",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LuxmonOptionsFlow:
        """Tell HA we have an options flow."""
        return LuxmonOptionsFlow(config_entry)


class LuxmonOptionsFlow(config_entries.OptionsFlow):
    """Options flow for lux-mon."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        options = self.config_entry.options

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
                ): int,
                vol.Optional(
                    CONF_DEVICE_ID,
                    default=options.get(CONF_DEVICE_ID, data.get(CONF_DEVICE_ID, "")),
                ): str,
                vol.Optional(
                    CONF_INVERTER_MODEL,
                    default=options.get(CONF_INVERTER_MODEL, data.get(CONF_INVERTER_MODEL, "")),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
