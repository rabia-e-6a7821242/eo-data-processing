#!/usr/bin/env bash
# Download the data, make the NetCDF/Zarr copies, run the benchmark and
# execute all notebooks (outputs are saved inside the .ipynb files).
# Usage (inside the eo-data conda environment):  bash scripts/run_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1. Download (skips files that already exist) =="
(cd scripts && python download.py)

echo "== 2. NetCDF -> Zarr copies =="
(cd scripts && python convert_formats.py)

echo "== 3. Benchmark =="
(cd scripts && python benchmark.py)

echo "== 4. Notebooks =="
cd notebooks
for nb in 01_era5_first_look 02_cloud_properties 03_cams_air_quality 04_netcdf_vs_zarr; do
    echo "   $nb"
    jupytext --to ipynb "$nb.py" -q
    jupyter nbconvert --to notebook --execute --inplace "$nb.ipynb"
done
echo "Done. Figures are in figures/"
