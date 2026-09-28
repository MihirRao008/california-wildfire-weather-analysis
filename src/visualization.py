"""Shared chart styling so every figure in the project looks consistent."""

import matplotlib.pyplot as plt

# Colors (a colorblind-checked palette).
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRAY = "#8a8985"
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
BACKGROUND = "#fcfcfb"
GRID = "#e4e3df"


def set_chart_style():
    """Apply a clean, readable style to all matplotlib charts."""
    plt.rcParams.update({
        "figure.figsize": (9, 5),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "figure.facecolor": BACKGROUND,
        "axes.facecolor": BACKGROUND,
        "savefig.facecolor": BACKGROUND,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_SECONDARY,
        "axes.titlecolor": TEXT,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": TEXT_SECONDARY,
        "ytick.color": TEXT_SECONDARY,
        "font.size": 10,
        "legend.frameon": False,
    })


def save_figure(fig, filename):
    """Save a figure into the project's figures/ folder."""
    fig.savefig(f"../figures/{filename}")
