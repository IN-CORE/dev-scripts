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
