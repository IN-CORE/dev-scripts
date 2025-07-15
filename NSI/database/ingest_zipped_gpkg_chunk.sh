#!/bin/bash

# Usage: ./ingest_zipped_gpkg_chunking.sh input_file.zip

set -e

# Load environment variables
source .env

INPUT_ZIP="$1"
SQL_FILE="nsi.sql"
POD_NAME="incore-postgresql-0"
CONTAINER_PATH="/bitnami/postgresql"
DB_NAME="nsi"
DB_USER="postgres"
CHUNK_PREFIX="nsi_part_"
CHUNK_LINES=200000
MAX_RETRIES=3
COPY_LOG="copy_chunks.log"

if [[ -z "$INPUT_ZIP" ]]; then
  echo "Usage: $0 <input_file.zip>"
  exit 1
fi

if [[ ! -f "$INPUT_ZIP" ]]; then
  echo "File not found: $INPUT_ZIP"
  exit 1
fi

# Clean up old chunk files
echo "Cleaning up old local chunks..."
rm -f ${CHUNK_PREFIX}*
rm -f "$SQL_FILE"

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

# Strip destructive SQL
sed -i '/DROP TABLE IF EXISTS/,/);/d' "$SQL_FILE"

# Remove unzipped .gpkg file
echo "Removing $UNZIPPED_GPKG..."
rm -f "$UNZIPPED_GPKG"

echo "3 second pause..."
sleep 3

# Split SQL into chunks by lines
echo "Splitting $SQL_FILE into $CHUNK_LINES-line chunks..."
split -l "$CHUNK_LINES" -d -a 2 "$SQL_FILE" "$CHUNK_PREFIX"

echo "3 second pause..."
sleep 3

# Clean up chunk files in pod
echo "Cleaning up old chunk files in pod..."
kubectl exec -it "$POD_NAME" -- bash -c "rm -f $CONTAINER_PATH/${CHUNK_PREFIX}*" || true

# Copy chunks to pod with retry, log progress
rm -f "$COPY_LOG"
touch "$COPY_LOG"
for f in ${CHUNK_PREFIX}*; do
  echo "Copying $f to pod..." | tee -a "$COPY_LOG"
  success=false
  for ((i=1; i<=MAX_RETRIES; i++)); do
    if kubectl cp "$f" "$POD_NAME:$CONTAINER_PATH/$f" >> "$COPY_LOG" 2>&1; then
      echo "Successfully copied $f (attempt $i)" | tee -a "$COPY_LOG"
      success=true
      break
    else
      echo "Failed to copy $f (attempt $i), retrying in $((i*2)) seconds..." | tee -a "$COPY_LOG"
      sleep $((i*2))
    fi
  done
  if ! $success; then
    echo "ERROR: Failed to copy $f after $MAX_RETRIES attempts." | tee -a "$COPY_LOG"
    exit 1
  fi
  sleep 2

done

# Execute SQL chunks in order
for f in ${CHUNK_PREFIX}*; do
  echo "Executing $f inside pod..."
  kubectl exec -it "$POD_NAME" -- bash -c \
    "PGPASSWORD=$POSTGRES_PASSWORD psql -U $DB_USER -d $DB_NAME -f $CONTAINER_PATH/$f"
  sleep 2
done

# Remove chunk files from pod
echo "Cleaning up chunk files in pod..."
kubectl exec -it "$POD_NAME" -- bash -c "rm -f $CONTAINER_PATH/${CHUNK_PREFIX}*"

# Remove local chunk files and SQL
echo "Cleaning up local chunk files and SQL..."
rm -f ${CHUNK_PREFIX}*
rm -f "$SQL_FILE"

echo "Done. File copy log saved to $COPY_LOG"
