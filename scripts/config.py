"""
config.py
Settings shared by all scripts and notebooks: study region, period,
variables and file paths. Change things here, not in the other files.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"          # files exactly as downloaded from Copernicus
ZARR = DATA / "zarr"        # converted copies
FIGS = ROOT / "figures"
RESULTS = ROOT / "results"

# Study region: Turkey and the Eastern Mediterranean
# CDS/ADS "area" order is [North, West, South, East]
AREA = [45, 20, 30, 50]

# Case-study month (spring: frontal clouds/rain and Saharan dust outbreaks)
YEAR = "2023"
MONTH = "04"

# ERA5 hourly single-level variables (CDS names -> short names in the file)
ERA5_VARIABLES = [
    "2m_temperature",                    # t2m   [K]
    "2m_dewpoint_temperature",           # d2m   [K]
    "mean_sea_level_pressure",           # msl   [Pa]
    "10m_u_component_of_wind",           # u10   [m s-1]
    "10m_v_component_of_wind",           # v10   [m s-1]
    "total_precipitation",               # tp    [m] (accumulated over 1 h)
    "total_cloud_cover",                 # tcc   [0-1]
    "low_cloud_cover",                   # lcc   [0-1]
    "medium_cloud_cover",                # mcc   [0-1]
    "high_cloud_cover",                  # hcc   [0-1]
    "total_column_cloud_liquid_water",   # tclw  [kg m-2]
    "total_column_cloud_ice_water",      # tciw  [kg m-2]
    "total_column_water_vapour",         # tcwv  [kg m-2]
    "land_sea_mask",                     # lsm   [0-1]
]

# CAMS global reanalysis (EAC4), 3-hourly, 0.75 deg
CAMS_VARIABLES = [
    "total_aerosol_optical_depth_550nm",   # aod550
    "dust_aerosol_optical_depth_550nm",    # duaod550
    "particulate_matter_2.5um",            # pm2p5 [kg m-3]
    "particulate_matter_10um",             # pm10  [kg m-3]
    "total_column_carbon_monoxide",        # tcco  [kg m-2]
]

# File names
ERA5_MONTH_NC = RAW / f"era5_single_levels_{YEAR}{MONTH}.nc"
CAMS_MONTH_NC = RAW / f"cams_eac4_{YEAR}{MONTH}.nc"
ERA5_T2M_YEAR_NC = RAW / f"era5_t2m_{YEAR}.nc"     # used for the NetCDF vs Zarr benchmark

# Cities used for time series (lat, lon)
CITIES = {
    "Istanbul": (41.0, 29.0),
    "Ankara": (39.9, 32.85),
    "Izmir": (38.4, 27.15),
    "Antalya": (36.9, 30.7),
    "Erzurum": (39.9, 41.27),
}

# Public cloud-native copy of ERA5 (Google ARCO-ERA5, no account needed)
ARCO_ERA5 = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
