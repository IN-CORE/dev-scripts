import duckdb

### get duckdb connection with spatial extension
def get_connection(db_file):
    conn = duckdb.connect(db_file, read_only=False)
    # checking spatial extention and install
    spatial_extension_query = conn.execute("SELECT * FROM duckdb_extensions() WHERE installed IS TRUE AND extension_name = 'spatial';").fetchone()
    if spatial_extension_query is None:
        print("Installing DuckDB spatial extension...")
        conn.execute("INSTALL spatial;")
    
    # loading spatial extension
    conn.execute("LOAD spatial;")
    return conn

### Create a database from a csv file
def create_db_with_shp(conn, shapefile):
    conn.execute(f"CREATE TABLE slc AS SELECT * FROM ST_READ('{shapefile}');") 

### Create a database from a csv file
def create_table_from_csv(conn, table_name, csv_file):
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv('{csv_file}');") 



if __name__ == "__main__":
    con = get_connection("slc_geo_data.db")

    #create_table_from_csv(con, "slc_bldg_ret_cost", "base-data/slc_bldg_retrofit_cost.csv")
    print(con.execute("select * from slc_bldg_ret_cost limit 5").fetchall())
    con.close()
