#!/bin/bash

# ------------------------------------------------------------------------------
# Script: run_ingest.sh
#
# Description:
#   This script batch-ingests multiple GeoJSON files into a PostgreSQL/PostGIS
#   database by calling `ingest_geojson_to_postgis.sh` for each file.
#   It is designed to loop through all files matching the pattern
#   chunks/chunk_*.geojson and ingest them one by one.
#
# Usage:
#   ./run_ingest.sh
#
# Requirements:
#   - The directory "chunks/" must contain GeoJSON files named in the pattern
#     chunk_*.geojson.
#   - The script `ingest_geojson_to_postgis.sh` must exist and be executable
#     in the same directory or in your PATH.
#
# Notes:
#   - Each file is imported using the "append" mode by default.
#   - Make sure the database is configured to handle repeated appends
#     and duplicate data, if applicable.
# ------------------------------------------------------------------------------


for file in chunks/chunk_*.geojson; do
  ./ingest_geojson_to_postgis.sh "$file" append
done
