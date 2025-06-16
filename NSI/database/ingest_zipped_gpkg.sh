#!/bin/bash
# ------------------------------------------------------------------------------
# Script: ingest_zipped_gpkg.sh
#
# Description:
#   This script ingests a zipped GeoPackage (.gpkg) file into a PostgreSQL/PostGIS
#   database running in a Kubernetes pod. It performs the following steps:
#
#     1. Unzips the input .zip file to extract the .gpkg file.
#     2. Converts the GeoPackage to a PostgreSQL-compatible SQL dump using `ogr2ogr`.
#     3. Strips out destructive SQL (DROP TABLE / CREATE TABLE).
#     4. Copies the SQL file into the target PostgreSQL pod.
#     5. Executes the SQL inside the pod to insert the data into the target table.
#     6. Cleans up temporary files both locally and inside the pod.
#
# Usage:
#   ./ingest_zipped_gpkg.sh <input_file.zip>
#
#   <input_file.zip>   A .zip archive containing a single .gpkg file.
#
# Requirements:
#   - GDAL with `ogr2ogr` and PGDump support.
#   - `kubectl` with access to the Kubernetes cluster.
#   - A `.env` file with at least `POSTGRES_PASSWORD` defined.
#
# Assumptions:
#   - PostgreSQL pod name is `incore-postgresql-0`.
#   - SQL is appended into an existing table named `nsi`.
#   - SQL and data are stored under `/bitnami/postgresql` in the pod.
#
# Notes:
#   - Automatically removes any unzipped or temporary files after execution.
#   - Skips failed records during conversion with `-skipfailures`.
# ------------------------------------------------------------------------------

# Usage: ./ingest_zipped_gpkg.sh input_file.zip

set -e

# Load environment variables (e.g., POSTGRES_PASSWORD)
source .env

INPUT_ZIP="$1"
UNZIPPED_GPKG=""
SQL_FILE="nsi.sql"
POD_NAME="incore-postgresql-0"
CONTAINER_PATH="/bitnami/postgresql"
DB_NAME="nsi"
DB_USER="postgres"

if [[ -z "$INPUT_ZIP" ]]; then
  echo "Usage: $0 <input_file.zip>"
  exit 1
fi

if [[ ! -f "$INPUT_ZIP" ]]; then
  echo "File not found: $INPUT_ZIP"
  exit 1
fi

# Unzip the GeoPackage file
echo "Unzipping $INPUT_ZIP..."
unzip -o "$INPUT_ZIP"
UNZIPPED_GPKG=$(unzip -Z1 "$INPUT_ZIP" | grep -i '\.gpkg$')

if [[ ! -f "$UNZIPPED_GPKG" ]]; then
  echo "Unzipped .gpkg file not found"
  exit 1
fi

# Convert to SQL
echo "Converting $UNZIPPED_GPKG to $SQL_FILE..."
ogr2ogr -f "PGDump" "$SQL_FILE" "$UNZIPPED_GPKG" \
  -nln nsi \
  -append \
  -lco GEOMETRY_NAME=geom \
  -skipfailures \
  -gt 65536
#  -nlt PROMOTE_TO_MULTI

# Strip destructive SQL
sed -i '/DROP TABLE IF EXISTS/,/);/d' "$SQL_FILE"

# Remove unzipped .gpkg file
echo "Removing $UNZIPPED_GPKG..."
rm -f "$UNZIPPED_GPKG"

# Copy SQL file into pod
echo "Copying $SQL_FILE to pod..."
kubectl cp "$SQL_FILE" "$POD_NAME:$CONTAINER_PATH/$SQL_FILE"

# Execute SQL in pod
echo "Executing SQL inside pod..."
kubectl exec -it "$POD_NAME" -- bash -c "PGPASSWORD=$POSTGRES_PASSWORD psql -U $DB_USER -d $DB_NAME -f $CONTAINER_PATH/$SQL_FILE"

# Remove SQL file from pod
echo "Removing $SQL_FILE from pod..."
kubectl exec -it "$POD_NAME" -- rm -f "$CONTAINER_PATH/$SQL_FILE"

# Remove SQL file locally
echo "Removing $SQL_FILE locally..."
rm -f "$SQL_FILE"

echo "Done."

