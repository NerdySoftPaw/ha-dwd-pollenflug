"""Config and options flow for DWD Pollenflug."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from . import DwdPollenflugConfigEntry
from .const import CONF_REGIONS, DOMAIN
from .coordinator import async_fetch

_LOGGER = logging.getLogger(__name__)


async def _region_options(hass) -> list[SelectOptionDict]:
    """Fetch the live region list to populate the selector."""
    session = async_get_clientsession(hass)
    data = await async_fetch(session)
    return [
        SelectOptionDict(value=str(region.region_id), label=region.name)
        for region in sorted(data.regions.values(), key=lambda r: r.name)
    ]


def _regions_schema(options: list[SelectOptionDict], selected: list[str]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_REGIONS, default=selected): SelectSelector(
                SelectSelectorConfig(
                    options=options,
                    multiple=True,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            )
        }
    )


class DwdPollenflugConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-entry config flow with multi-region selection."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        try:
            options = await _region_options(self.hass)
        except (aiohttp.ClientError, TimeoutError, KeyError, ValueError):
            _LOGGER.exception("Could not load DWD region list")
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            return self.async_create_entry(
                title="DWD Pollenflug",
                data={CONF_REGIONS: user_input[CONF_REGIONS]},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_regions_schema(options, []),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: DwdPollenflugConfigEntry,
    ) -> DwdPollenflugOptionsFlow:
        return DwdPollenflugOptionsFlow()


class DwdPollenflugOptionsFlow(OptionsFlow):
    """Change the set of monitored regions after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        try:
            options = await _region_options(self.hass)
        except (aiohttp.ClientError, TimeoutError, KeyError, ValueError):
            return self.async_abort(reason="cannot_connect")

        current: list[str] = self.config_entry.options.get(
            CONF_REGIONS, self.config_entry.data.get(CONF_REGIONS, [])
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_regions_schema(options, current),
        )
