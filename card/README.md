# DWD Pollenflug Card

A self-contained Lovelace card for the `dwd_pollenflug` integration. No build
step, no dependencies — a single plain custom element.

![row layout: icon · name · level bar · today/tomorrow/in-2-days chips]

## Install

1. Copy `dwd-pollenflug-card.js` into your Home Assistant `config/www/` folder
   (e.g. `config/www/dwd-pollenflug-card.js`).
2. Register it as a dashboard resource — **Settings → Dashboards → ⋮ → Resources
   → Add**:
   - URL: `/local/dwd-pollenflug-card.js`
   - Type: **JavaScript Module**

   (Or in YAML mode, under `lovelace: resources:` add
   `{ url: /local/dwd-pollenflug-card.js, type: module }`.)
3. Hard-refresh the browser (Ctrl/Cmd+Shift+R).

## Usage

```yaml
type: custom:dwd-pollenflug-card
title: Pollenflug – Inseln und Marschen   # optional; auto-derived from the device
forecast: true                            # optional (default true): morgen/übermorgen chips
entities:
  - sensor.<region>_grasses
  - sensor.<region>_birch
  - sensor.<region>_hazel
  - sensor.<region>_alder
  - sensor.<region>_ash
  - sensor.<region>_rye
  - sensor.<region>_mugwort
  - sensor.<region>_ragweed
```

Tip: open **Developer Tools → States**, filter for your region's sensors, and
copy the exact `entity_id`s. You can list as many or as few pollen types as you
like, and override a label with `{ entity: sensor.x, name: "Custom" }`.

## What it shows

- Per pollen type: icon, name, a colour-coded level bar (index `0`–`3`, green →
  red), and the German burden description for **today**.
- Optional chips for **Heute / Morgen / Übermorgen** with a colour dot and the
  index band (e.g. `2–3`); hover for the description.
- Footer: DWD `last_update` timestamp and attribution.

Colours follow the DWD scale: `0` green · `1` light green · `1.5` amber · `2`
orange · `3` red (half-steps interpolated).
