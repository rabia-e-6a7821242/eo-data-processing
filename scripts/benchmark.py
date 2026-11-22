"""
benchmark.py
Measures how fast the same data can be read from the NetCDF and Zarr copies
made by convert_formats.py. Four typical tasks are timed:

  open     open the dataset (read only the metadata)
  map      read ONE time step for the whole region  (e.g. to draw a map)
  series   read the WHOLE YEAR at ONE grid point    (e.g. a station time series)
  monthly  compute monthly means of the whole dataset (reads everything)

Each task is repeated N_REPEAT times on a freshly opened dataset and the
median time is kept. Note: after the first run the files are in the Linux
page cache (RAM), so these are "warm cache" timings; the differences between
formats come mostly from how much data has to be decompressed and copied.

Usage (from the repository root):
    python scripts/benchmark.py
"""

import statistics
import time
from pathlib import Path

import pandas as pd
import xarray as xr

import config as cfg
from convert_formats import OUT, time_name

N_REPEAT = 5
LAT, LON = cfg.CITIES["Ankara"]


def open_any(path):
    if str(path).endswith(".zarr"):
        return xr.open_zarr(path, chunks=None, consolidated=False)
    return xr.open_dataset(path, chunks=None)


def timed(func, path):
    times = []
    for _ in range(N_REPEAT):
        t0 = time.perf_counter()
        func(path)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def task_open(path):
    open_any(path).close()


def task_map(path):
    ds = open_any(path)
    ds["t2m"].isel({time_name(ds): 4000}).values
    ds.close()


def task_series(path):
    ds = open_any(path)
    ds["t2m"].sel(latitude=LAT, longitude=LON, method="nearest").values
    ds.close()


def task_monthly(path):
    ds = open_any(path)
    ds["t2m"].resample({time_name(ds): "1MS"}).mean().values
    ds.close()


def disk_usage(path):
    path = Path(path)
    if path.is_file():
        return path.stat().st_size, 1
    files = [f for f in path.rglob("*") if f.is_file()]
    return sum(f.stat().st_size for f in files), len(files)


def chunk_shape(path):
    ds = open_any(path)
    var = ds["t2m"]
    shape = var.encoding.get("chunks") or var.encoding.get("chunksizes")
    ds.close()
    return "contiguous" if not shape else "x".join(str(s) for s in shape)


def main():
    rows = []
    for name, path in OUT.items():
        size, n_files = disk_usage(path)
        row = {"format": name, "size_MB": size / 1e6, "n_files": n_files,
               "chunks (time x lat x lon)": chunk_shape(path)}
        for task in (task_open, task_map, task_series, task_monthly):
            row[task.__name__.replace("task_", "") + "_s"] = timed(task, path)
        rows.append(row)
        print(row)

    df = pd.DataFrame(rows)
    cfg.RESULTS.mkdir(exist_ok=True)
    df.to_csv(cfg.RESULTS / "benchmark.csv", index=False, float_format="%.4f")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
