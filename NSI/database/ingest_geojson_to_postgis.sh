# ------------------------------------------------------------------------------
# Script: ingest_geojson_to_pog
#
# Description:
#   This script imports a GeoJSON file into a PostgreSQL/PostGIS database
#   running inside a Kubernetes cluster. It sets up a port-forward to the
#   database service, then uses `ogr2ogr` to ingest the data into a specified
#   table.
#
# Usage:
#   ./ingest_geojson_to_pog <geojson-file> [overwrite|append]
#
#   <geojson-file>   Path to the GeoJSON file to import.
#   [overwrite|append]  Optional mode for import. Defaults to "append".
#                       - overwrite: Drops and recreates the target table.
#                       - append: Appends data to the existing table.
#
# Configuration:
#   The script assumes the PostgreSQL service is accessible via Kubernetes,
#   and that `kubectl`, `ogr2ogr`, and PostgreSQL client tools are installed.
#   Database and Kubernetes details (e.g., namespace, service name) are defined
#   in the configuration section of the script.
#
# Dependencies:
#   - kubectl (for port-forwarding)
#   - ogr2ogr (from GDAL)
#
# Note:
#   The script will temporarily forward a local port to the Kubernetes service,
#   then terminate the forwarding after the operation is complete.
# ------------------------------------------------------------------------------


#!/bin/bash

# === CHECK ARGUMENTS ===
if [ -z "$1" ]; then
  echo "Usage: $0 <geojson-file> [overwrite|append]"
  exit 1
fi

GEOJSON_FILE="$1"
IMPORT_MODE=${2:-append}  # Default to "append" if not specified

# === CONFIGURATION ===
NAMESPACE="incore"
SERVICE_NAME="incore-postgresql"
LOCAL_PORT="54321"
REMOTE_PORT="5432"
DB_NAME="nsi"
DB_USER="postgres"
DB_PASSWORD="password"
TABLE_NAME="nsi"

# === START PORT-FORWARD ===
echo "Starting port-forward to PostgreSQL in Kubernetes..."
kubectl port-forward -n "$NAMESPACE" "services/$SERVICE_NAME" $LOCAL_PORT:$REMOTE_PORT > /dev/null 2>&1 &
PORT_FORWARD_PID=$!
echo "Port-forward PID: $PORT_FORWARD_PID"

# Wait for port-forward to establish
sleep 5

# === RUN ogr2ogr TO IMPORT GEOJSON ===
echo "Ingesting GeoJSON ($GEOJSON_FILE) into PostGIS table '$TABLE_NAME' with mode '$IMPORT_MODE'..."
PGPASSWORD=$DB_PASSWORD ogr2ogr -f "PostgreSQL" PG:"host=localhost port=$LOCAL_PORT dbname=$DB_NAME user=$DB_USER" \
  -nln "$TABLE_NAME" -$IMPORT_MODE -lco GEOMETRY_NAME=geometry "$GEOJSON_FILE"

# Check for success
if [ $? -eq 0 ]; then
  echo "GeoJSON successfully imported to '$TABLE_NAME'."
else
  echo "Error: GeoJSON import failed."
fi

# === STOP PORT-FORWARD ===
echo "Stopping port-forward..."
kill $PORT_FORWARD_PID

echo "Done."
