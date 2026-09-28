# Data Dictionary

Columns in the final analysis table, `data/processed/wildfires_with_weather.csv`, which is created by
`notebooks/02_data_cleaning.ipynb`. The table has one row per wildfire: 251,880 California fires from 1992–2020.

## Fire information (from FPA FOD, USDA Forest Service)

| Column | Type | Description | Original FPA FOD column |
|---|---|---|---|
| `fire_id` | integer | Unique record ID | `FOD_ID` |
| `fire_name` | text | Fire name, uppercase. `UNNAMED` if missing (19% of records) | `FIRE_NAME` |
| `discovery_date` | date | Date the fire was discovered | `DISCOVERY_DATE` |
| `fire_year` | integer | Year of discovery | `FIRE_YEAR` |
| `fire_month` | integer | Month of discovery (1–12) | derived |
| `fire_season` | text | Winter (Dec–Feb), Spring (Mar–May), Summer (Jun–Aug), Fall (Sep–Nov) | derived |
| `county` | text | County name without the word "County". `Unknown` if missing (38%) | `FIPS_NAME` |
| `latitude`, `longitude` | decimal degrees | Fire's point of origin | `LATITUDE`, `LONGITUDE` |
| `cause_class` | text | Human, Natural, or Missing/undetermined | `NWCG_CAUSE_CLASSIFICATION` |
| `cause` | text | General cause category (e.g. Equipment and vehicle use, Natural, Arson) | `NWCG_GENERAL_CAUSE` |
| `land_owner` | text | Owner of the land where the fire started | `OWNER_DESCR` |
| `fire_size_acres` | decimal (acres) | Final fire size | `FIRE_SIZE` |
| `fire_size_class` | A–G | NWCG size class. A ≤ 0.25, B 0.26–9.9, C 10–99.9, D 100–299, E 300–999, F 1,000–4,999, G 5,000+ acres | `FIRE_SIZE_CLASS` |
| `log_fire_size` | decimal | `log(1 + fire_size_acres)`, used because fire size is extremely skewed | derived |
| `is_large_fire` | True/False | True if `fire_size_acres` ≥ 100 (classes D–G) | derived |

## Weather information (from the NASA POWER Daily API, MERRA-2)

These values are the weather at the NASA grid point nearest the fire, on the discovery date.

| Column | Type | Description | NASA parameter and conversion |
|---|---|---|---|
| `cell_lat`, `cell_lon` | degrees | Nearest NASA grid point. The grid spacing is 0.5° latitude × 0.625° longitude | derived |
| `temp_max_f` | °F | Maximum air temperature at 2 m | `T2M_MAX` (°C) × 9/5 + 32 |
| `relative_humidity` | % | Daily average relative humidity at 2 m | `RH2M` |
| `wind_speed_mph` | mph | Daily average wind speed at 2 m | `WS2M` (m/s) × 2.23694 |
| `precip_mm` | mm | Precipitation on the discovery date | `PRECTOTCORR` |
| `precip_prev_7day_mm` | mm | Total precipitation over the 7 days before the discovery date | sum of `PRECTOTCORR` |

## Raw files (`data/raw/`, not on GitHub)

| File | Source | Size |
|---|---|---|
| `FPA_FOD_20221014.sqlite` | Forest Service archive, SQLite format | 958 MB |
| `_variable_descriptions.csv` | Same download. The official description of each FPA FOD column | 10 KB |
| `nasa_power_daily_ca.csv` | Created by `src/download_weather.py`. 176 grid points × 10,624 days (Dec 1991 – Dec 2020) | 77 MB |
