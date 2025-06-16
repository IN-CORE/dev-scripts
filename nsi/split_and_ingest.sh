#!/bin/bash

# === CHECK ARGUMENTS ===
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <geojson-file> <layer-name>"
  exit 1
fi

INPUT_FILE="$1"
LAYER_NAME="$2"
FEATURES_PER_FILE=10000

# === CONFIGURATION ===
NAMESPACE="incore"
SERVICE_NAME="incore-postgresql"
LOCAL_PORT="54321"
REMOTE_PORT="5432"
DB_NAME="nsi"
DB_USER="postgres"
DB_PASSWORD="password"  # Replace or prompt
TABLE_NAME="nsi"

# === STEP 1: GET TOTAL FEATURE COUNT ===
TOTAL_FEATURES=$(ogrinfo -ro -al -geom=NO "$INPUT_FILE" "$LAYER_NAME" | grep "Feature Count:" | cut -d: -f2 | xargs)

if [ -z "$TOTAL_FEATURES" ]; then
  echo "Failed to determine feature count. Exiting."
  exit 1
fi

echo "Splitting $INPUT_FILE into chunks of $FEATURES_PER_FILE features..."
mkdir -p chunks
rm -f chunks/chunk_*.geojson

COUNT=0
START_INDEX=0

while [ $START_INDEX -lt $TOTAL_FEATURES ]; do
  OUT_FILE=$(printf "chunks/chunk_%03d.geojson" $COUNT)
  END_INDEX=$((START_INDEX + FEATURES_PER_FILE))

  ogr2ogr -f GeoJSON "$OUT_FILE" "$INPUT_FILE" "$LAYER_NAME" \
    -where "fid >= $START_INDEX AND fid < $END_INDEX"

  if [ $? -ne 0 ]; then
    echo "Error creating $OUT_FILE"
    break
  fi

  echo "Created $OUT_FILE"
  COUNT=$((COUNT + 1))
  START_INDEX=$END_INDEX
done


# === STEP 2: PORT-FORWARD TO POSTGRESQL ===
echo "Starting port-forward to PostgreSQL in Kubernetes..."
kubectl port-forward -n "$NAMESPACE" "services/$SERVICE_NAME" $LOCAL_PORT:$REMOTE_PORT > /dev/null 2>&1 &
PORT_FORWARD_PID=$!
sleep 5

# === STEP 3: IMPORT EACH CHUNK ===
CHUNK_INDEX=0
for FILE in chunks/chunk_*.geojson; do
  echo "Importing $FILE into table '$TABLE_NAME'..."
  IMPORT_MODE="append"
  if [ $CHUNK_INDEX -eq 0 ]; then
    IMPORT_MODE="overwrite"
  fi

  PGPASSWORD=$DB_PASSWORD ogr2ogr -f "PostgreSQL" \
    PG:"host=localhost port=$LOCAL_PORT dbname=$DB_NAME user=$DB_USER" \
    -nln "$TABLE_NAME" -$IMPORT_MODE -lco GEOMETRY_NAME=geometry "$FILE"

  if [ $? -ne 0 ]; then
    echo "Error importing $FILE"
    break
  fi

  CHUNK_INDEX=$((CHUNK_INDEX + 1))
done

# === STEP 4: STOP PORT-FORWARDING ===
echo "Stopping port-forward..."
kill $PORT_FORWARD_PID

echo "Done."
