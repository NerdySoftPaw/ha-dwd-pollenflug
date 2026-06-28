"""The DWD Pollenflug integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import DwdPollenflugCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type DwdPollenflugConfigEntry = ConfigEntry[DwdPollenflugCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: DwdPollenflugConfigEntry
) -> bool:
    """Set up DWD Pollenflug from a config entry."""
    coordinator = DwdPollenflugCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: DwdPollenflugConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(
    hass: HomeAssistant, entry: DwdPollenflugConfigEntry
) -> None:
    """Reload entry when the selected regions change (options flow)."""
    await hass.config_entries.async_reload(entry.entry_id)
