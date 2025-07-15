"""
Script: query.py

Description:
    This script provides example functions to test and perform queries on the
    `nsi_raw` table stored in a PostgreSQL/PostGIS database. It includes:

    - A simple connection test to validate database connectivity.
    - A FIPS-based spatial query to extract NSI data for a specific county.
    - A bounding box (BBOX) query (example shown, but currently uses an invalid SQL condition).

Usage:
    python query.py

Functions:
    - connection_test_raw(): Checks if the database connection is successful by selecting one row.
    - query_test_fips(): Fetches features by a specific FIPS code and writes the result to a GeoPackage.
    - query_test_bbox(): Placeholder for bounding-box-based spatial query (SQL statement needs correction).

Requirements:
    - Python packages: geopandas, sqlalchemy
    - Local module: NsiUtils with `df_to_geopkg()` method
    - Config file: config.Config with database credentials and host info

Notes:
    - The current BBOX query is not valid SQL. Consider replacing:
        WHERE bbox=%s
      with:
        WHERE ST_Within(geometry, ST_MakeEnvelope(..., 4326))
"""

import geopandas as gp

from sqlalchemy import create_engine
from config import Config as cfg
from nsiutils import NsiUtils

# create the sqlalchemy connection engine
db_connection_url = "postgresql://%s:%s@%s:%s/%s" % \
                    (cfg.DB_USERNAME, cfg.DB_PASSWORD, cfg.DB_URL, cfg.DB_PORT, cfg.DB_NAME)
table_name = "public.nsi_raw"

def connection_test_raw():
    con = create_engine(db_connection_url)

    # check the connection
    cursor = con.execute("SELECT * FROM public.nsi_raw;")
    cursor.next()

    con.dispose()


def query_test_fips():
    test_fips = '21017'
    query_str = "SELECT * FROM %s WHERE fips='%s';" % (table_name, test_fips)
    gdf = gp.GeoDataFrame.from_postgis(
        query_str, db_connection_url, geom_col='geometry', index_col='fd_id', coerce_float=True)

    outfile = "data\\test_" + test_fips + ".gpkg"

    NsiUtils.df_to_geopkg(gdf, outfile)


def query_test_bbox():
    bbox='-84.297,38.246,-84.297,38.261,-84.123,38.261,-84.123,38.246,-84.297,38.246'
    query_str = "SELECT * FROM %s WHERE bbox=%s;" % (table_name, bbox)
    gdf = gp.GeoDataFrame.from_postgis(
        query_str, db_connection_url, geom_col='geometry', index_col='fd_id', coerce_float=True)

    outfile = "data\\test_bbox.gpkg"

    NsiUtils.df_to_geopkg(gdf, outfile)


if __name__ == '__main__':
    query_test_bbox()
