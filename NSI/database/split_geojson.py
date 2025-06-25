#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# Script: split_geojson.py
#
# Description:
#   This script splits a large GeoJSON file into smaller chunks, each containing
#   a fixed number of features (default: 10,000), and saves them as separate
#   GeoJSON files.
#
# Usage:
#   python split_geojson.py <input-geojson-file> <features-per-file>
#
#   <input-geojson-file>    Path to the large GeoJSON file to split.
#   <features-per-file>     Optional. Number of features per output file.
#                           Defaults to 10,000 if not provided.
#
# Requirements:
#   - Python 3
#   - geopandas
#
# Notes:
#   - Output files are saved in the `chunks/` directory as chunk_000.geojson,
#     chunk_001.geojson, etc.
#   - The input GeoJSON must be small enough to fit in memory if using GeoPandas.
# ------------------------------------------------------------------------------

import geopandas as gpd
import os
import sys
import shutil

# === Check for command-line argument ===
if len(sys.argv) < 2:
    print("Usage: python split_geojson_chunks.py <geojson-file>")
    sys.exit(1)

input_file = sys.argv[1]
chunk_size = 10000

# === Load GeoJSON ===
gdf = gpd.read_file(input_file)
total = len(gdf)
print(f"Total features: {total}")

# === Clean and prepare output directory ===
chunk_dir = "chunks"
if os.path.exists(chunk_dir):
    shutil.rmtree(chunk_dir)
os.makedirs(chunk_dir)

# === Split and save chunks ===
for i in range(0, total, chunk_size):
    chunk = gdf.iloc[i:i+chunk_size]
    out_file = os.path.join(chunk_dir, f"chunk_{i // chunk_size:03}.geojson")
    chunk.to_file(out_file, driver="GeoJSON")
    print(f"Wrote {out_file}")


