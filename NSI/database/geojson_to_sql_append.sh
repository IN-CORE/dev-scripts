#!/bin/bash
# ------------------------------------------------------------------------------
# Script: geojson_to_sql_append.sh
#
# Description:
#   This script converts a GeoJSON file into a PostgreSQL-compatible SQL dump
#   that is safe to append to an existing PostGIS table named `nsi`.
#
#   It uses `ogr2ogr` with PGDump format to generate SQL, strips out table
#   creation and deletion statements, and produces a SQL file (`nsi.sql`)
#   containing only INSERT and geometry-related data.
#
# Usage:
#   ./geojson_to_sql_append.sh <input.geojson>
#
#   <input.geojson>   Path to the GeoJSON file to convert.
#
# Output:
#   nsi.sql           SQL file that can be safely appended to an existing table.
#
# Requirements:
#   - GDAL with `ogr2ogr` and PGDump support.
#
# Notes:
#   - Output uses `geom` as the geometry column name.
#   - The generated SQL file skips failed records and disables automatic FID.
#   - Drop/Create table statements are stripped automatically.
# ------------------------------------------------------------------------------


set -e

INPUT_GEOJSON="$1"
OUTPUT_SQL="nsi.sql"

if [[ -z "$INPUT_GEOJSON" ]]; then
  echo "Usage: $0 <input.geojson>"
  exit 1
fi

if [[ ! -f "$INPUT_GEOJSON" ]]; then
  echo "File not found: $INPUT_GEOJSON"
  exit 1
fi

echo "Converting $INPUT_GEOJSON to $OUTPUT_SQL..."

ogr2ogr -f "PGDump" "$OUTPUT_SQL" "$INPUT_GEOJSON" \
  -nln nsi \
  -append \
  -lco GEOMETRY_NAME=geom \
  -unsetFid \
  -skipfailures \
  -gt 65536

echo "Stripping DROP TABLE and CREATE TABLE statements..."

# Remove the DROP TABLE line
#sed -i '/^DROP TABLE IF EXISTS nsi;/d' "$OUTPUT_SQL"

# Remove the CREATE TABLE block
#sed -i '/^CREATE TABLE nsi/,/^);/d' "$OUTPUT_SQL"

# Remove the DROP TABLE and CREATE TABLE block safely
# Remove DROP TABLE and CREATE TABLE block completely
sed -i '/DROP TABLE IF EXISTS/,/);/d' "$OUTPUT_SQL"


echo "Done: $OUTPUT_SQL is ready to append safely."
