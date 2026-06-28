"""DataUpdateCoordinator for the DWD pollen forecast."""

from __future__ import annotations

import asyncio
import logging

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MAX_INTERVAL, MIN_INTERVAL, UPDATE_BUFFER, URL
from .model import PollenflugData, parse

_LOGGER = logging.getLogger(__name__)


async def async_fetch(session: aiohttp.ClientSession) -> PollenflugData:
    """Fetch and parse the DWD pollen forecast once."""
    async with asyncio.timeout(30):
        response = await session.get(URL)
        response.raise_for_status()
        # DWD serves the file as text/plain, so disable content-type checking.
        raw = await response.json(content_type=None)
    return parse(raw)


class DwdPollenflugCoordinator(DataUpdateCoordinator[PollenflugData]):
    """Fetches the whole pollen forecast once and shares it with all sensors."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=MIN_INTERVAL,
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> PollenflugData:
        try:
            data = await async_fetch(self._session)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error fetching DWD pollen data: {err}") from err
        except (KeyError, ValueError) as err:
            raise UpdateFailed(f"Error parsing DWD pollen data: {err}") from err

        # The data only changes once a day — poll again shortly after DWD's
        # announced next update instead of hammering the endpoint hourly.
        self.update_interval = self._next_interval(data)
        return data

    @staticmethod
    def _next_interval(data: PollenflugData):
        delay = data.next_update + UPDATE_BUFFER - dt_util.now()
        if delay < MIN_INTERVAL:
            return MIN_INTERVAL
        if delay > MAX_INTERVAL:
            return MAX_INTERVAL
        return delay
