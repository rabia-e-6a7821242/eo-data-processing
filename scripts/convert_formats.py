"""
convert_formats.py
Makes different on-disk copies of the same ERA5 2 m temperature data
(one full year, hourly) so that NetCDF and Zarr can be compared fairly.

The *data* are identical in every copy, only the file format, chunk shape
and compression change:

  netcdf_cds          the file exactly as downloaded from CDS
  netcdf_contiguous   NetCDF4, no chunks, no compression
  zarr_map_chunks     Zarr, one chunk = 1 day of full maps   (time=24, lat=all, lon=all)
  zarr_series_chunks  Zarr, one chunk = 1 year at 10x10 points (time=all, lat=10, lon=10)

Usage (from the repository root, after download.py t2m_year):
    python scripts/convert_formats.py
"""

import shutil

import xarray as xr

import config as cfg

OUT = {
    "netcdf_cds": cfg.ERA5_T2M_YEAR_NC,
    "netcdf_contiguous": cfg.ZARR.parent / "converted" / "t2m_contiguous.nc",
    "zarr_map_chunks": cfg.ZARR / "t2m_map_chunks.zarr",
    "zarr_series_chunks": cfg.ZARR / "t2m_series_chunks.zarr",
}


def time_name(ds):
    """New CDS files call the time coordinate 'valid_time', older ones 'time'."""
    return "valid_time" if "valid_time" in ds.dims else "time"


def main():
    ds = xr.open_dataset(cfg.ERA5_T2M_YEAR_NC)
    t = time_name(ds)
    # drop the small helper coordinates that CDS adds (number, expver)
    ds = ds.drop_vars([v for v in ("number", "expver") if v in ds.variables])
    ds = ds.load()
    print(ds)

    # NetCDF4 without chunking and compression
    path = OUT["netcdf_contiguous"]
    path.parent.mkdir(parents=True, exist_ok=True)
    enc = {v: {"contiguous": True, "zlib": False, "chunksizes": None} for v in ds.data_vars}
    ds.to_netcdf(path, encoding=enc)
    print("wrote", path)

    # Zarr copies with two different chunk shapes (default compression of zarr 3: zstd)
    chunkings = {
        "zarr_map_chunks": {t: 24, "latitude": -1, "longitude": -1},
        "zarr_series_chunks": {t: -1, "latitude": 10, "longitude": 10},
    }
    for name, chunks in chunkings.items():
        path = OUT[name]
        if path.exists():
            shutil.rmtree(path)
        ds_c = ds.chunk(chunks)
        for v in ds_c.variables:          # remove NetCDF-specific encoding
            ds_c[v].encoding = {}
        ds_c.to_zarr(path, mode="w", zarr_format=3, consolidated=False)
        print("wrote", path)


if __name__ == "__main__":
    main()
