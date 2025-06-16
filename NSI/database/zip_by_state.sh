#!/bin/bash
# ------------------------------------------------------------------------------
# Script: zip_by_state.sh
#
# Description:
#   This script batch-zips all `.geojson` files in the current directory.
#   For each file, it creates a corresponding `.zip` archive named after the
#   base filename (e.g., `CA.geojson` becomes `CA.zip`).
#
# Usage:
#   ./zip_by_state.sh
#
# Requirements:
#   - bash
#   - zip
#
# Notes:
#   - Existing .zip files with the same name will be overwritten without prompt.
# ------------------------------------------------------------------------------

for file in *.geojson; do
  # Extract the filename without extension
  name="${file%.geojson}"
  # Create a zip file named after the state
  zip "${name}.zip" "$file"
done
