"""Constants for the DWD Pollenflug integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "dwd_pollenflug"

# Config / options keys.
CONF_REGIONS = "regions"

# DWD open-data endpoint (no API key, no rate limit).
URL = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"

ATTRIBUTION = "Daten vom Deutschen Wetterdienst (DWD)"

# DWD refreshes once per day around 11:00 local time. We schedule the next poll
# shortly after the announced next_update, clamped to this range.
UPDATE_BUFFER = timedelta(minutes=20)
MIN_INTERVAL = timedelta(hours=1)
MAX_INTERVAL = timedelta(hours=24)
