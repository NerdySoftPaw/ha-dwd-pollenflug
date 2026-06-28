# DWD Pollenflug (Home Assistant)

Pollen forecast sensors for Germany, sourced from the **Deutscher Wetterdienst (DWD)**
open-data [`s31fg.json`](https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json)
feed — no API key, no rate limit.

A modern, async rewrite of the original
[`hacs_dwd_pollenflug`](https://github.com/mampfes/hacs_dwd_pollenflug) integration.

## What you get

- 8 pollen sensors per region: Hazel, Alder, Ash, Birch, Grasses, Rye, Mugwort, Ragweed
- Index `0`–`3` (transitional bands like `2-3` map to `2.5`) for **today**, with
  `tomorrow` and `in 2 days` plus German descriptions as attributes
- One device per selected region; pick any of the 27 (part-)regions

## Why it's different from the original

| | Original | This integration |
|---|---|---|
| HTTP | `requests` (blocking) | `aiohttp`, fully async |
| Updates | hand-rolled hourly polling + manual per-entity updates | single `DataUpdateCoordinator`, one fetch shared by all sensors |
| Poll cadence | every hour | scheduled right after DWD's announced `next_update` (data changes once/day) |
| Dependencies | `pytz` | none (stdlib `zoneinfo` + HA's `aiohttp`) |
| Config | one config entry per region | one entry, multi-region select + options flow |
| Naming / i18n | raw `Pollenflug Graeser 11` | `has_entity_name` + translation keys (DE/EN) |
| Extras | — | diagnostics, unit tests for the parser |

## Installation

**HACS (custom repository):** add `https://github.com/NerdySoftPaw/ha-dwd-pollenflug` as an *Integration*, install, restart HA.

**Manual:** copy `custom_components/dwd_pollenflug` into your HA `config/custom_components/`, restart.

Then **Settings → Devices & Services → Add Integration → DWD Pollenflug** and select your regions.

## Sensor state

The state is today's index for that pollen type:

| Index | Belastung |
|---|---|
| 0 | keine |
| 0.5 | keine bis gering |
| 1 | gering |
| 1.5 | gering bis mittel |
| 2 | mittel |
| 2.5 | mittel bis hoch |
| 3 | hoch |

Attributes: `state_tomorrow`, `state_in_2_days`, the matching `*_desc` German
texts, plus `last_update` / `next_update`.

## Development

```bash
pip install pytest
pytest tests/            # parser tests, no Home Assistant needed
```

## Data source & licence

Data: Deutscher Wetterdienst, *Pollenflug-Gefahrenindex*. See the
[format description (PDF)](https://opendata.dwd.de/climate_environment/health/alerts/Beschreibung_pollen_s31fg.pdf).
Integration code: MIT.
