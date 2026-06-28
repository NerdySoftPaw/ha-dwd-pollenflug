"""Pure data model and parser for the DWD pollen forecast.

This module has *no* Home Assistant dependencies on purpose, so the parsing
logic can be unit-tested in isolation (see ``tests/test_model.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from zoneinfo import ZoneInfo

# DWD publishes timestamps as e.g. "2026-06-28 11:00 Uhr" in local German time.
_TIME_FORMAT = "%Y-%m-%d %H:%M Uhr"
_TZ = ZoneInfo("Europe/Berlin")

# Keys used inside each region's "Pollen" block, mapped to a day offset.
_PREDICTION_KEYS: dict[str, int] = {
    "today": 0,
    "tomorrow": 1,
    "dayafter_to": 2,
}

# Pollen species in the order DWD lists them.
POLLEN_TYPES: tuple[str, ...] = (
    "Hasel",
    "Erle",
    "Esche",
    "Birke",
    "Graeser",
    "Roggen",
    "Beifuss",
    "Ambrosia",
)


def to_value(raw: str | None) -> float | None:
    """Convert a DWD index string to a float.

    ``"0"`` -> 0.0, ``"2-3"`` -> 2.5 (mid-point of a transitional band),
    ``"-1"`` / ``""`` / ``None`` -> ``None`` (no data).
    """
    if raw is None:
        return None
    raw = raw.strip()
    if raw in ("", "-1"):
        return None
    if "-" in raw:
        low, high = raw.split("-", 1)
        return (float(low) + float(high)) / 2
    return float(raw)


@dataclass(frozen=True, slots=True)
class RegionInfo:
    """A selectable (part-)region."""

    region_id: int
    name: str


@dataclass(frozen=True, slots=True)
class Forecast:
    """Index values for a single pollen type in a single region."""

    today: float | None
    tomorrow: float | None
    dayafter: float | None


@dataclass(slots=True)
class PollenflugData:
    """Fully parsed snapshot of the DWD pollen forecast."""

    last_update: datetime
    next_update: datetime
    name: str
    sender: str
    legend: dict[float, str]
    regions: dict[int, RegionInfo] = field(default_factory=dict)
    # forecasts[region_id][pollen_type] -> Forecast
    forecasts: dict[int, dict[str, Forecast]] = field(default_factory=dict)

    @property
    def today(self) -> date:
        """The day the 'today' values refer to (DWD local date)."""
        return self.last_update.date()


def _region_key(entry: dict) -> int:
    """Stable id for a region; falls back to the parent region when there is
    no part-region (``partregion_id == -1``)."""
    return entry["region_id"] if entry["partregion_id"] == -1 else entry["partregion_id"]


def _region_name(entry: dict) -> str:
    if entry["partregion_id"] == -1:
        return entry["region_name"]
    return f"{entry['region_name']} – {entry['partregion_name']}"


def _parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, _TIME_FORMAT).replace(tzinfo=_TZ)


def _parse_legend(legend: dict[str, str]) -> dict[float, str]:
    """Map each numeric index to its human-readable German description."""
    out: dict[float, str] = {}
    for key, value in legend.items():
        if key.endswith("_desc"):
            continue
        numeric = to_value(value)
        if numeric is not None:
            out[numeric] = legend[f"{key}_desc"]
    return out


def parse(raw: dict) -> PollenflugData:
    """Parse the raw ``s31fg.json`` payload into :class:`PollenflugData`."""
    regions: dict[int, RegionInfo] = {}
    forecasts: dict[int, dict[str, Forecast]] = {}

    for entry in raw["content"]:
        key = _region_key(entry)
        regions[key] = RegionInfo(key, _region_name(entry))
        forecasts[key] = {
            pollen: Forecast(
                today=to_value(pred.get("today")),
                tomorrow=to_value(pred.get("tomorrow")),
                dayafter=to_value(pred.get("dayafter_to")),
            )
            for pollen, pred in entry["Pollen"].items()
        }

    return PollenflugData(
        last_update=_parse_timestamp(raw["last_update"]),
        next_update=_parse_timestamp(raw["next_update"]),
        name=raw["name"],
        sender=raw["sender"],
        legend=_parse_legend(raw["legend"]),
        regions=regions,
        forecasts=forecasts,
    )
