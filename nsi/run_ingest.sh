for file in chunks/chunk_*.geojson; do
  ./ingest_geojson_to_postgis.sh "$file"
done
