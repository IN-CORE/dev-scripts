import geopandas as gpd
import os

input_file = "AL.geojson"
chunk_size = 10000

gdf = gpd.read_file(input_file)
total = len(gdf)
print(f"Total features: {total}")

os.makedirs("chunks", exist_ok=True)

for i in range(0, total, chunk_size):
    chunk = gdf.iloc[i:i+chunk_size]
    out_file = f"chunks/chunk_{i//chunk_size:03}.geojson"
    chunk.to_file(out_file, driver="GeoJSON")
    print(f"Wrote {out_file}")

