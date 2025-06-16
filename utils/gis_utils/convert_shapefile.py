# import geopandas as gpd
import geobuf
import json
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd


def convert_shapefile_to_geojson(in_shapefile, output_file):
    # Read the Shapefile into a GeoDataFrame
    gdf = gpd.read_file(in_shapefile)

    # Convert GeoDataFrame to GeoJSON format
    geojson = gdf.to_crs(epsg='4326').to_json()

    # Write GeoJSON to a file
    with open(output_file, 'w') as f:
        f.write(geojson)


def convert_geojson_to_shapefile(in_geojson, output_file):
    # Read the GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file(in_geojson)

    # Write GeoDataFrame to a Shapefile
    gdf.to_file(output_file, driver='ESRI Shapefile')


def convert_geojson_to_geobuf(geojson_file, geobuf_file):
    # Read GeoJSON file
    with open(geojson_file, 'r') as f:
        geojson_data = f.read()

    # Parse GeoJSON string into a Python dictionary
    geojson_dict = json.loads(geojson_data)

    # Convert GeoJSON dictionary to Geobuf
    geobuf_data = geobuf.encode(geojson_dict)

    # Write Geobuf data to a file
    with open(geobuf_file, 'wb') as f:
        f.write(geobuf_data)


def convert_shapefile_to_geobuf(in_shapefile, output_file):
    # Read the Shapefile into a GeoDataFrame
    gdf = gpd.read_file(in_shapefile)

    # Convert GeoDataFrame to GeoJSON format
    geojson = gdf.to_crs(epsg='4326').to_json()

    # Parse GeoJSON string into a Python dictionary
    geojson_dict = json.loads(geojson)

    # Convert GeoJSON dictionary to Geobuf
    geobuf_data = geobuf.encode(geojson_dict)

    # Write Geobuf data to a file
    with open(output_file, 'wb') as f:
        f.write(geobuf_data)


def convert_geojson_to_geoparquet(geojson_file, output_file):
    # Read GeoJSON file
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)

    # Convert GeoJSON to pandas DataFrame
    df = pd.json_normalize(geojson_data['features'])

    # Write DataFrame to Parquet file
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_file)


if __name__ == "__main__":
    shapefile = "epn.shp"
    geojson_file = "slc_building.geojson"
    geobuf_file = "epn.pbf"
    geoparquet_file = "slc_bldg.geoparquet"

    # to convert shapefile to geojson
    # convert_shapefile_to_geojson(shapefile, geojson_file)

    # to convert geojson to shapefile
    # convert_geojson_to_shapefile(geojson_file, shapefile)

    # to convert geojson to geobuf
    # convert_geojson_to_geobuf(geojson_file, geobuf_file)

    # to convert geojson to geoparquet
    convert_geojson_to_geoparquet(geojson_file, geoparquet_file)

