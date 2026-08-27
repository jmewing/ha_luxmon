"""Config flow for lux-mon integration."""
from __future__ import annotations

import logging
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


class LuxmonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for lux-mon."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

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
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                vol.Optional("api_token"): str,
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
