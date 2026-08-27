"""Tests for lux-mon global services."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.luxmon import (
    DOMAIN,
    SERVICE_LOAD_AUTOMATION_RULES,
    SERVICE_QUICK_CHARGE_START,
    SERVICE_QUICK_CHARGE_STOP,
    SERVICE_SET_SETTING,
    async_setup,
)


@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.data = {DOMAIN: {}}
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    return hass


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator._client.quick_charge_start = AsyncMock(return_value={"ok": True})
    coordinator._client.quick_charge_stop = AsyncMock(return_value={"ok": True})
    coordinator._client.set_setting = AsyncMock(return_value={"updated": True})
    coordinator._client.load_automation_rules = AsyncMock(return_value={"saved": True})
    coordinator._session = MagicMock()
    return coordinator


@pytest.mark.asyncio
async def test_services_registered(mock_hass):
    result = await async_setup(mock_hass, {})
    assert result is True
    calls = mock_hass.services.async_register.call_args_list
    names = {call.args[1] for call in calls}
    assert SERVICE_QUICK_CHARGE_START in names
    assert SERVICE_QUICK_CHARGE_STOP in names
    assert SERVICE_SET_SETTING in names
    assert SERVICE_LOAD_AUTOMATION_RULES in names


@pytest.mark.asyncio
async def test_quick_charge_start_handler(mock_hass, mock_coordinator):
    mock_hass.data[DOMAIN]["entry-1"] = mock_coordinator
    await async_setup(mock_hass, {})

    call = MagicMock()
    call.data = {"amps": 80, "minutes": 45}
    # Find the registered handler for quick_charge_start
    for registered in mock_hass.services.async_register.call_args_list:
        if registered.args[1] == SERVICE_QUICK_CHARGE_START:
            handler = registered.args[2]
            await handler(call)
            break
    mock_coordinator._client.quick_charge_start.assert_awaited_once_with(
        mock_coordinator._session, amps=80, minutes=45
    )


@pytest.mark.asyncio
async def test_quick_charge_stop_handler(mock_hass, mock_coordinator):
    mock_hass.data[DOMAIN]["entry-1"] = mock_coordinator
    await async_setup(mock_hass, {})

    call = MagicMock()
    call.data = {}
    for registered in mock_hass.services.async_register.call_args_list:
        if registered.args[1] == SERVICE_QUICK_CHARGE_STOP:
            handler = registered.args[2]
            await handler(call)
            break
    mock_coordinator._client.quick_charge_stop.assert_awaited_once_with(mock_coordinator._session)


@pytest.mark.asyncio
async def test_set_setting_handler(mock_hass, mock_coordinator):
    mock_hass.data[DOMAIN]["entry-1"] = mock_coordinator
    await async_setup(mock_hass, {})

    call = MagicMock()
    call.data = {"name": "output_source_priority", "value": "sbu"}
    for registered in mock_hass.services.async_register.call_args_list:
        if registered.args[1] == SERVICE_SET_SETTING:
            handler = registered.args[2]
            await handler(call)
            break
    mock_coordinator._client.set_setting.assert_awaited_once_with(
        mock_coordinator._session, "output_source_priority", "sbu"
    )


@pytest.mark.asyncio
async def test_load_automation_rules_handler(mock_hass, mock_coordinator):
    mock_hass.data[DOMAIN]["entry-1"] = mock_coordinator
    await async_setup(mock_hass, {})

    rules = [{"type": "rule_table", "target": "ac_charge_battery_current", "rows": []}]
    call = MagicMock()
    call.data = {"rules": rules, "enabled": True}
    for registered in mock_hass.services.async_register.call_args_list:
        if registered.args[1] == SERVICE_LOAD_AUTOMATION_RULES:
            handler = registered.args[2]
            await handler(call)
            break
    mock_coordinator._client.load_automation_rules.assert_awaited_once_with(
        mock_coordinator._session, rules, enabled=True
    )
