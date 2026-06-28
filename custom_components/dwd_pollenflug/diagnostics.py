"""Diagnostics support for DWD Pollenflug."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import DwdPollenflugConfigEntry
from .const import CONF_REGIONS


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: DwdPollenflugConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    data = coordinator.data
    return {
        "last_update": data.last_update.isoformat(),
        "next_update": data.next_update.isoformat(),
        "update_interval": str(coordinator.update_interval),
        "selected_regions": entry.options.get(
            CONF_REGIONS, entry.data.get(CONF_REGIONS, [])
        ),
        "available_regions": {
            str(rid): region.name for rid, region in data.regions.items()
        },
    }
