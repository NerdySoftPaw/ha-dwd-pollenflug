"""Sensor platform for DWD Pollenflug."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DwdPollenflugConfigEntry
from .const import ATTRIBUTION, CONF_REGIONS, DOMAIN, URL
from .coordinator import DwdPollenflugCoordinator
from .model import POLLEN_TYPES, Forecast


@dataclass(frozen=True, kw_only=True)
class PollenSensorEntityDescription(SensorEntityDescription):
    """Sensor description carrying the DWD pollen key."""

    pollen_key: str


SENSOR_DESCRIPTIONS: tuple[PollenSensorEntityDescription, ...] = tuple(
    PollenSensorEntityDescription(
        key=pollen.lower(),
        translation_key=pollen.lower(),
        pollen_key=pollen,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for pollen in POLLEN_TYPES
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DwdPollenflugConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the pollen sensors for every selected region."""
    coordinator = entry.runtime_data
    selected: list[str] = entry.options.get(
        CONF_REGIONS, entry.data.get(CONF_REGIONS, [])
    )

    entities: list[PollenflugSensor] = []
    for raw_id in selected:
        region_id = int(raw_id)
        if region_id not in coordinator.data.regions:
            continue
        entities.extend(
            PollenflugSensor(coordinator, region_id, description)
            for description in SENSOR_DESCRIPTIONS
        )

    async_add_entities(entities)


class PollenflugSensor(CoordinatorEntity[DwdPollenflugCoordinator], SensorEntity):
    """A single pollen-type sensor for one region."""

    entity_description: PollenSensorEntityDescription
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: DwdPollenflugCoordinator,
        region_id: int,
        description: PollenSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._region_id = region_id
        self._attr_unique_id = f"{DOMAIN}_{region_id}_{description.key}"

        region = coordinator.data.regions[region_id]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(region_id))},
            name=region.name,
            manufacturer=coordinator.data.sender,
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=URL,
        )

    @property
    def _forecast(self) -> Forecast | None:
        return self.coordinator.data.forecasts.get(self._region_id, {}).get(
            self.entity_description.pollen_key
        )

    @property
    def available(self) -> bool:
        forecast = self._forecast
        return super().available and forecast is not None and forecast.today is not None

    @property
    def native_value(self) -> float | None:
        forecast = self._forecast
        return forecast.today if forecast else None

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:
        forecast = self._forecast
        if forecast is None:
            return None
        data = self.coordinator.data
        legend = data.legend
        return {
            "state_today_desc": legend.get(forecast.today),
            "state_tomorrow": forecast.tomorrow,
            "state_tomorrow_desc": legend.get(forecast.tomorrow),
            "state_in_2_days": forecast.dayafter,
            "state_in_2_days_desc": legend.get(forecast.dayafter),
            "last_update": data.last_update.isoformat(),
            "next_update": data.next_update.isoformat(),
        }
