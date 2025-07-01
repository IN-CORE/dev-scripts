#!/bin/bash

# Usage: ./ingest_zipped_gpkg_chunking.sh input_file.zip

set -e

# Load environment variables (e.g., POSTGRES_PASSWORD)
source .env

INPUT_ZIP="$1"
UNZIPPED_GPKG=""
SQL_FILE="nsi.sql"
CHUNK_PREFIX="nsi_part_"
CHUNK_SIZE=250m
COPY_LOG="copy_chunks.log"
POD_NAME="incore-postgresql-0"
CONTAINER_PATH="/bitnami/postgresql"
DB_NAME="nsi"
DB_USER="postgres"
MAX_RETRIES=3

# Check input zip
if [[ -z "$INPUT_ZIP" ]]; then
  echo "Usage: $0 <input_file.zip>"
  exit 1
fi

if [[ ! -f "$INPUT_ZIP" ]]; then
  echo "File not found: $INPUT_ZIP"
  exit 1
fi

# Cleanup any old local chunks
echo "Cleaning up old local chunks..."
rm -f ${CHUNK_PREFIX}*

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

echo "3 second pause..."
sleep 3

# Split SQL into smaller chunks
echo "Splitting $SQL_FILE into $CHUNK_SIZE chunks..."
split -b "$CHUNK_SIZE" -d -a 2 "$SQL_FILE" "$CHUNK_PREFIX"

# Clean up old chunk files in pod
echo "Cleaning up old chunk files in pod..."
kubectl exec -it "$POD_NAME" -- bash -c "rm -f $CONTAINER_PATH/${CHUNK_PREFIX}* || true"

echo "2 second pause..."
sleep 2

# Initialize or clear log
echo "Starting chunk copy log: $(date)" > "$COPY_LOG"

# Copy chunks to pod with retry and log
for f in ${CHUNK_PREFIX}*; do
  echo "Copying $f to pod..." | tee -a "$COPY_LOG"
  success=false
  for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "Attempt $i: kubectl cp $f to pod..." >> "$COPY_LOG"
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
done

echo "5 second pause before executing SQL in pod..."
sleep 5

# Execute SQL chunks in order
for f in ${CHUNK_PREFIX}*; do
  echo "Executing $f inside pod..."
  kubectl exec -i "$POD_NAME" -- bash -c \
    "PGPASSWORD=$POSTGRES_PASSWORD psql -U $DB_USER -d $DB_NAME -f $CONTAINER_PATH/$f"
  sleep 2
done

# Remove SQL chunks from pod
echo "Removing SQL chunks from pod..."
kubectl exec -it "$POD_NAME" -- bash -c "rm -f $CONTAINER_PATH/${CHUNK_PREFIX}*"

# Remove SQL chunks locally
echo "Removing local SQL chunks..."
rm -f ${CHUNK_PREFIX}*

# Remove main SQL file
echo "Removing $SQL_FILE..."
rm -f "$SQL_FILE"

echo "Done."
