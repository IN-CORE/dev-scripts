import geopandas as gp
from sqlalchemy import create_engine
from config import Config as cfg

# create the sqlalchemy connection engine
db_connection_url = "postgresql://%s:%s@%s:%s/%s" % \
                    (cfg.DB_USERNAME, cfg.DB_PASSWORD, cfg.DB_URL, cfg.DB_PORT, cfg.DB_NAME)


def connection_test_raw():
    con = create_engine(db_connection_url)

    # check the connection
    cursor = con.execute("SELECT * FROM public.nsi_raw;")
    cursor.next()

    con.dispose()


def connection_test():
    test_fips = '290970112004033'
    query_str = "SELECT * FROM public.nsi_raw WHERE cbfips='%s';" % (test_fips)
    gdf = gp.GeoDataFrame.from_postgis(
        query_str, db_connection_url, geom_col='geometry', index_col='fd_id', coerce_float=True)

    outfile = "data\\test.gpkg"

    gdf.to_file(outfile, driver="GPKG")


if __name__ == '__main__':
    connection_test()
