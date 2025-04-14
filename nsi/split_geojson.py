import geopandas as gpd
import os
import sys
import shutil

# === Check for command-line argument ===
if len(sys.argv) < 2:
    print("Usage: python split_geojson_chunks.py <geojson-file>")
    sys.exit(1)

input_file = sys.argv[1]
chunk_size = 10000

# === Load GeoJSON ===
gdf = gpd.read_file(input_file)
total = len(gdf)
print(f"Total features: {total}")

# === Clean and prepare output directory ===
chunk_dir = "chunks"
if os.path.exists(chunk_dir):
    shutil.rmtree(chunk_dir)
os.makedirs(chunk_dir)

# === Split and save chunks ===
for i in range(0, total, chunk_size):
    chunk = gdf.iloc[i:i+chunk_size]
    out_file = os.path.join(chunk_dir, f"chunk_{i // chunk_size:03}.geojson")
    chunk.to_file(out_file, driver="GeoJSON")
    print(f"Wrote {out_file}")


