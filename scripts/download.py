"""
download.py
Downloads the data used in this project from the Copernicus data stores
with the official `cdsapi` client.

  ERA5   -> Climate Data Store (CDS),     key in ~/.cdsapirc
  CAMS   -> Atmosphere Data Store (ADS),  key in ~/.adsapirc

Before the first download you must accept the dataset licences on the
CDS and ADS websites (see README). Requests can wait in a queue for a few
minutes, this is normal.

Usage (from the repository root):
    python scripts/download.py            # everything
    python scripts/download.py era5       # only the ERA5 month
    python scripts/download.py cams       # only CAMS
    python scripts/download.py t2m_year   # only the 1-year t2m file for the benchmark
"""

import sys
import zipfile
from pathlib import Path

import cdsapi
import xarray as xr

import config as cfg

HOURS = [f"{h:02d}:00" for h in range(24)]


def client_from(rc_file):
    """Make a cdsapi client from a 'url: ... / key: ...' file."""
    values = {}
    for line in Path(rc_file).expanduser().read_text().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            values[k.strip()] = v.strip()
    return cdsapi.Client(url=values["url"], key=values["key"])


def unzip_if_needed(path):
    """The new CDS returns a zip with several NetCDF files when a request mixes
    instantaneous and accumulated variables (e.g. t2m and tp). In that case
    merge them into a single NetCDF file."""
    if not zipfile.is_zipfile(path):
        return
    print(f"  {path.name} is a zip archive, merging the files inside it")
    tmp = path.with_suffix(".zip")
    path.rename(tmp)
    folder = tmp.with_suffix("")
    with zipfile.ZipFile(tmp) as z:
        z.extractall(folder)
    parts = [xr.open_dataset(f) for f in sorted(folder.glob("*.nc"))]
    xr.merge(parts, compat="override").to_netcdf(path)
    for p in parts:
        p.close()
    for f in folder.glob("*"):
        f.unlink()
    folder.rmdir()
    tmp.unlink()


def get_era5_month():
    client_from("~/.cdsapirc").retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": ["reanalysis"],
            "variable": cfg.ERA5_VARIABLES,
            "year": [cfg.YEAR],
            "month": [cfg.MONTH],
            "day": [f"{d:02d}" for d in range(1, 31)],
            "time": HOURS,
            "area": cfg.AREA,
            "data_format": "netcdf",
            "download_format": "unarchived",
        },
        str(cfg.ERA5_MONTH_NC),
    )
    unzip_if_needed(cfg.ERA5_MONTH_NC)


def get_t2m_year():
    client_from("~/.cdsapirc").retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": ["reanalysis"],
            "variable": ["2m_temperature"],
            "year": [cfg.YEAR],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": HOURS,
            "area": cfg.AREA,
            "data_format": "netcdf",
            "download_format": "unarchived",
        },
        str(cfg.ERA5_T2M_YEAR_NC),
    )
    unzip_if_needed(cfg.ERA5_T2M_YEAR_NC)


def get_cams_month():
    client_from("~/.adsapirc").retrieve(
        "cams-global-reanalysis-eac4",
        {
            "variable": cfg.CAMS_VARIABLES,
            "date": [f"{cfg.YEAR}-{cfg.MONTH}-01/{cfg.YEAR}-{cfg.MONTH}-30"],
            "time": [f"{h:02d}:00" for h in range(0, 24, 3)],
            "area": cfg.AREA,
            "data_format": "netcdf",
        },
        str(cfg.CAMS_MONTH_NC),
    )
    unzip_if_needed(cfg.CAMS_MONTH_NC)


JOBS = {"era5": (get_era5_month, cfg.ERA5_MONTH_NC),
        "cams": (get_cams_month, cfg.CAMS_MONTH_NC),
        "t2m_year": (get_t2m_year, cfg.ERA5_T2M_YEAR_NC)}

if __name__ == "__main__":
    cfg.RAW.mkdir(parents=True, exist_ok=True)
    wanted = sys.argv[1:] or list(JOBS)
    for name in wanted:
        func, target = JOBS[name]
        if target.exists():
            print(f"{target.name} already exists, skipping")
            continue
        print(f"Downloading {name} -> {target}")
        func()
        print(f"  done, {target.stat().st_size / 1e6:.1f} MB")
