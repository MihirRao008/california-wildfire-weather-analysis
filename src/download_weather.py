"""Download daily NASA POWER weather for every grid cell that contains a California fire.

Run from the project root (after downloading the wildfire database):

    python src/download_weather.py

It writes data/raw/nasa_power_daily_ca.csv. No API key is needed.
Takes roughly 5-10 minutes (one request per grid cell, about 180 cells).
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).parent))
from data_cleaning import add_grid_cell_columns, load_california_fires

API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = ["T2M_MAX", "RH2M", "WS2M", "PRECTOTCORR"]
START_DATE = "19911201"  # a month early so we can compute rain in the week before Jan 1992 fires
END_DATE = "20201231"

DATABASE_PATH = "data/raw/FPA_FOD_20221014.sqlite"
OUTPUT_PATH = "data/raw/nasa_power_daily_ca.csv"


def download_cell(lat, lon):
    """Request the full daily history for one grid point and return it as a DataFrame."""
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": START_DATE,
        "end": END_DATE,
        "format": "JSON",
    }
    response = requests.get(API_URL, params=params, timeout=120)
    response.raise_for_status()
    values = response.json()["properties"]["parameter"]

    cell = pd.DataFrame(values)            # one row per date, one column per parameter
    cell.index.name = "date"
    cell = cell.reset_index()
    cell.insert(0, "cell_lat", lat)
    cell.insert(1, "cell_lon", lon)
    return cell


def main():
    fires = load_california_fires(DATABASE_PATH)
    fires = fires.rename(columns={"LATITUDE": "latitude", "LONGITUDE": "longitude"})
    fires = add_grid_cell_columns(fires)
    cells = fires[["cell_lat", "cell_lon"]].drop_duplicates().sort_values(["cell_lat", "cell_lon"])
    print(f"Downloading weather for {len(cells)} grid cells...")

    all_cells = []
    for number, (lat, lon) in enumerate(cells.itertuples(index=False), start=1):
        for attempt in range(3):
            try:
                all_cells.append(download_cell(lat, lon))
                break
            except requests.RequestException as error:
                print(f"  cell ({lat}, {lon}) attempt {attempt + 1} failed: {error}")
                time.sleep(5)
        print(f"  {number}/{len(cells)} done", end="\r")

    weather = pd.concat(all_cells, ignore_index=True)
    weather.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(weather):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
