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
def create_table_with_shp(conn, table_name, shapefile):
    con.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM ST_READ('{shapefile}');") 

### Create a database from a csv file
def create_table_from_csv(conn, table_name, csv_file):
    con.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv('{csv_file}');") 



if __name__ == "__main__":
    con = get_connection("rs_data.db")
    #create_table_with_shp(con, "slc", "base-data/slc_bldg_council2.shp")
    #create_table_with_shp(con, "galveston", "base-data/galveston_bldg_bnd.shp")
    #create_table_from_csv(con, "galveston_bldg_ret_cost", "base-data/galveston_elev_unit_cost.csv")

    #create_table_from_csv(con, "slc_bldg_ret_cost", "base-data/slc_bldg_retrofit_cost2.csv")

    #table_name = "joplin"

    #create_table_with_shp(con, "joplin", "base-data/joplin_bldg.shp")
    #print(con.execute(f"select * from {table_name} limit 5;").fetchall())
    #print(con.execute(f"select COUNT(guid) from {table_name};").fetchall())

    table_name = "joplin_bldg_ret_cost"

    #create_table_from_csv(con, "joplin_bldg_ret_cost", "base-data/joplin_retrofit_unit_cost.csv")
    create_table_from_csv(con, "joplin_bldg_ret_cost", "base-data/joplin_retrofit_cost.csv")
    print(con.execute(f"select * from {table_name} limit 5;").fetchall())

    print(con.execute("show tables;").fetchall())

    con.close()
