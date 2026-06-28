"""Unit tests for the pure DWD parser (no Home Assistant required)."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

# Make the integration importable without installing it.
sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "custom_components" / "dwd_pollenflug")
)

from model import parse, to_value  # noqa: E402

FIXTURE = Path(__file__).with_name("fixture_s31fg.json")


@pytest.fixture
def data():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parse(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", 0.0),
        ("3", 3.0),
        ("2-3", 2.5),
        ("0-1", 0.5),
        ("-1", None),
        ("", None),
        (None, None),
        ("  1-2 ", 1.5),
    ],
)
def test_to_value(raw, expected):
    assert to_value(raw) == expected


def test_timestamps_are_timezone_aware(data):
    assert data.last_update.tzinfo is not None
    assert data.next_update > data.last_update
    assert data.today == date(2026, 6, 28)


def test_regions_parsed(data):
    assert len(data.regions) == 2
    # part-region id is used as the key when present
    assert 11 in data.regions
    assert "Inseln und Marschen" in data.regions[11].name


def test_legend_maps_values_to_descriptions(data):
    assert data.legend[0.0] == "keine Belastung"
    assert data.legend[2.5] == "mittlere bis hohe Belastung"


def test_forecast_values(data):
    forecast = data.forecasts[11]["Graeser"]
    assert forecast.today == 2.5
    assert forecast.tomorrow == 2.5
    assert forecast.dayafter == 2.5

    none_forecast = data.forecasts[11]["Ambrosia"]
    assert none_forecast.today == 0.0


def test_all_pollen_types_present(data):
    for region in data.forecasts.values():
        assert set(region) >= {"Hasel", "Birke", "Graeser", "Ambrosia"}
