"""
helpers.py
Small helper functions used by the notebooks (opening files, unit
conversions, map plotting), so the notebooks stay short and readable.
"""

import time

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

import config as cfg

PLATE = ccrs.PlateCarree()

plt.rcParams.update({
    "figure.dpi": 100, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e0",
})

# fixed categorical colours (colour-blind checked order) and a neutral grey
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
GREY = "#8a8985"


def open_era5(path=cfg.ERA5_MONTH_NC):
    """Open an ERA5 file from the new CDS and tidy it up:
    rename 'valid_time' -> 'time' and drop the helper coords 'number'/'expver'."""
    ds = xr.open_dataset(path)
    if "valid_time" in ds.dims:
        ds = ds.rename({"valid_time": "time"})
    return ds.drop_vars([v for v in ("number", "expver") if v in ds.variables])


def open_cams(path=cfg.CAMS_MONTH_NC):
    ds = xr.open_dataset(path)
    if "valid_time" in ds.dims:
        ds = ds.rename({"valid_time": "time"})
    return ds.drop_vars([v for v in ("number", "expver") if v in ds.variables])


def map_axes(nrows=1, ncols=1, figsize=(7, 4.2)):
    """Figure with cartopy map axes over the study region."""
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize,
                             subplot_kw={"projection": PLATE}, squeeze=False)
    west, east = cfg.AREA[1], cfg.AREA[3]
    south, north = cfg.AREA[2], cfg.AREA[0]
    for ax in axes.flat:
        ax.set_extent([west, east, south, north], crs=PLATE)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
        ax.add_feature(cfeature.BORDERS, linewidth=0.4, edgecolor="#555555")
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="#bbbbbb")
        gl.top_labels = gl.right_labels = False
        gl.xlabel_style = gl.ylabel_style = {"size": 8}
    if axes.size == 1:
        return fig, axes[0, 0]
    if nrows == 1 or ncols == 1:
        return fig, axes.ravel()      # 1-D array: axes[0], axes[1], ...
    return fig, axes


def plot_field(da, ax, cmap="viridis", label="", **kwargs):
    """Filled map of a 2-D (latitude, longitude) DataArray with a colour bar."""
    im = da.plot.pcolormesh(ax=ax, transform=PLATE, cmap=cmap,
                            add_colorbar=False, **kwargs)
    plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02, label=label)
    return im


def save(fig, name):
    cfg.FIGS.mkdir(exist_ok=True)
    fig.savefig(cfg.FIGS / name)


def relative_humidity(t2m_k, d2m_k):
    """Relative humidity [%] from temperature and dew point (Magnus formula,
    coefficients of Alduchov and Eskridge, 1996)."""
    t, td = t2m_k - 273.15, d2m_k - 273.15
    a, b = 17.625, 243.04
    return 100 * np.exp(a * td / (b + td)) / np.exp(a * t / (b + t))


class Timer:
    """with Timer() as t: ...   ->  t.seconds"""
    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.seconds = time.perf_counter() - self.t0
