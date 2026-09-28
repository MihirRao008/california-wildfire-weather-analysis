"""Functions for loading and cleaning the wildfire and weather datasets.

Used by notebooks/02_data_cleaning.ipynb.
"""

import sqlite3

import numpy as np
import pandas as pd

# NASA POWER meteorology comes from the MERRA-2 model grid:
# one grid point every 0.5 degrees of latitude and 0.625 degrees of longitude.
GRID_LAT_STEP = 0.5
GRID_LON_STEP = 0.625

# Rough bounding box around California (degrees).
CA_LAT_MIN, CA_LAT_MAX = 32.5, 42.1
CA_LON_MIN, CA_LON_MAX = -124.5, -114.0

# Fires of at least this many acres are "large" (NWCG size classes D through G).
LARGE_FIRE_ACRES = 100


def load_california_fires(database_path):
    """Load California fire records from the FPA FOD SQLite database."""
    query = """
        SELECT
            FOD_ID, FIRE_NAME, FIRE_YEAR, DISCOVERY_DATE,
            NWCG_CAUSE_CLASSIFICATION, NWCG_GENERAL_CAUSE,
            FIRE_SIZE, FIRE_SIZE_CLASS, LATITUDE, LONGITUDE,
            OWNER_DESCR, STATE, FIPS_NAME
        FROM Fires
        WHERE STATE = 'CA'
    """
    connection = sqlite3.connect(database_path)
    fires = pd.read_sql_query(query, connection)
    connection.close()
    return fires


def month_to_season(month):
    """Convert a month number (1-12) to a meteorological season name."""
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Fall"


def nearest_grid_point(values, step, origin):
    """Snap coordinates to the nearest point on a regular grid.

    Example: with step=0.5 and origin=-90, latitude 39.81 becomes 40.0.
    """
    return (np.round((values - origin) / step) * step + origin).round(3)


def add_grid_cell_columns(fires):
    """Add the NASA POWER grid point (cell_lat, cell_lon) nearest to each fire."""
    fires = fires.copy()
    fires["cell_lat"] = nearest_grid_point(fires["latitude"], GRID_LAT_STEP, -90)
    fires["cell_lon"] = nearest_grid_point(fires["longitude"], GRID_LON_STEP, -180)
    return fires


def clean_weather(weather):
    """Clean the raw NASA POWER daily table and convert units."""
    weather = weather.copy()

    # NASA POWER marks missing values with -999.
    weather = weather.replace(-999, np.nan)

    weather["date"] = pd.to_datetime(weather["date"].astype(str), format="%Y%m%d")

    # Convert to US units that are easier to interpret.
    weather["temp_max_f"] = weather["T2M_MAX"] * 9 / 5 + 32
    weather["relative_humidity"] = weather["RH2M"]
    weather["wind_speed_mph"] = weather["WS2M"] * 2.23694
    weather["precip_mm"] = weather["PRECTOTCORR"]

    weather = weather.sort_values(["cell_lat", "cell_lon", "date"])

    # Total rain over the 7 days BEFORE each date (not including that day).
    # shift(1) moves each value down one day so today's rain is excluded.
    weather["precip_prev_7day_mm"] = (
        weather.groupby(["cell_lat", "cell_lon"])["precip_mm"]
        .transform(lambda series: series.shift(1).rolling(7).sum())
    )

    keep = ["cell_lat", "cell_lon", "date", "temp_max_f", "relative_humidity",
            "wind_speed_mph", "precip_mm", "precip_prev_7day_mm"]
    return weather[keep]
