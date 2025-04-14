
#!/bin/bash

# === CHECK ARGUMENT ===
if [ -z "$1" ]; then
  echo "Usage: $0 <geojson-file>"
  exit 1
fi

GEOJSON_FILE="$1"

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
echo "Ingesting GeoJSON ($GEOJSON_FILE) into PostGIS table '$TABLE_NAME'..."
PGPASSWORD=$DB_PASSWORD ogr2ogr -f "PostgreSQL" PG:"host=localhost port=$LOCAL_PORT dbname=$DB_NAME user=$DB_USER" \
  -nln "$TABLE_NAME" -overwrite -lco GEOMETRY_NAME=geometry "$GEOJSON_FILE"

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