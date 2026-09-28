"""Small helper functions for the statistical analysis."""

import pandas as pd

WEATHER_COLUMNS = ["temp_max_f", "relative_humidity", "wind_speed_mph",
                   "precip_mm", "precip_prev_7day_mm"]


def correlation_table(data, target, columns=WEATHER_COLUMNS):
    """Pearson and Spearman correlation of each column with the target column."""
    rows = []
    for column in columns:
        pair = data[[column, target]].dropna()
        rows.append({
            "variable": column,
            "pearson_r": pair[column].corr(pair[target], method="pearson"),
            "spearman_rho": pair[column].corr(pair[target], method="spearman"),
            "n": len(pair),
        })
    return pd.DataFrame(rows)


def summarize_by_bins(data, column, target, n_bins=10):
    """Split a weather variable into equal-sized groups (deciles) and summarize fire size.

    Returns one row per group with the group's middle value, the median fire size,
    and the share of fires that became large.
    """
    binned = data[[column, target, "is_large_fire"]].dropna().copy()
    binned["bin"] = pd.qcut(binned[column], q=n_bins, duplicates="drop")
    summary = binned.groupby("bin", observed=True).agg(
        bin_median=(column, "median"),
        median_fire_acres=(target, "median"),
        share_large=("is_large_fire", "mean"),
        n_fires=(target, "size"),
    ).reset_index(drop=True)
    return summary
