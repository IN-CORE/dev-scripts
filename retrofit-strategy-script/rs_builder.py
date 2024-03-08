import duckdb
import geopandas as gpd
import pandas as pd
import argparse
import json
import retrofit_cost_slc as rc_slc


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

### Get all the buildings in a specific boundary with a specific structure type
def get_buildings(conn, struct_typ, bnd_name):
    rel = conn.sql(f"SELECT guid, ST_AsText(geom) as geom FROM slc WHERE struct_typ='{struct_typ.upper()}' AND name='{bnd_name.upper()}';")
    print("# of buildings selected:", rel.shape[0])
    # gdf = gpd.GeoDataFrame(df,geometry= gpd.GeoSeries.from_wkt(df['geom']),crs="EPSG:4326")
    return rel


### create a retrofit strategy file from a list of buildings and retrofit strategies
def create_retrofit_strategy_by_rule(idx, rel, percent, retrofit_key, retrofit_val):
    df = rel.to_df()
    # selecting randm buildings with percent
    df_sample = df.sample(frac=percent/100.0)

    # add retrofit key and value to the dataframe
    idx_list = [idx] * df_sample.shape[0]
    key_list = [retrofit_key] * df_sample.shape[0]
    val_list = [retrofit_val] * df_sample.shape[0]
    df_sample['retrofit_key'] = key_list
    df_sample['retrofit_value'] = val_list
    df_sample['rule'] = idx_list

    print("# of buildings sampled:", df_sample.shape[0], "/", df.shape[0])

    return df_sample

def merge_create_retrofit_strategy(df_list, result_name):
    df = pd.concat(df_list)
    print(df.shape)
    df[['guid','retrofit_key','retrofit_value']].to_csv(result_name + ".csv", index=False)
    return df

def create_geo_retrofit_strategy(df, result_name):
    gdf = gpd.GeoDataFrame(df,geometry= gpd.GeoSeries.from_wkt(df['geom']),crs="EPSG:4326")
    gdf.drop(columns=['geom'], inplace=True)
    gdf.to_file(result_name + ".shp")
    return gdf

### Parse the retrofit strategy rules
def parse_rules(rules_str):
    rules = json.loads(rules_str)
    return rules

### Parse the retrofits
def parse_retrofits(retrofits_str):
    retrofits = json.loads(retrofits_str)
    return retrofits




if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description='Generating Retrofit Strategy Dataset')
    # parser.add_argument('--result_name', dest='result_name', help='Result name')
    # parser.add_argument('--rules', dest='rules', type=json.loads, help='Retrofit strategy rules')
    # parser.add_argument('--retrofits', dest='retrofits', type=json.loads, help='Retrofits')

    # args = parser.parse_args()

    # rules = parse_rules(args.rules_str)
    # retrofits = parse_rules(args.retrofits_str) 

    result_name = "retrofit_strategy_slc"

    rules = {
        "testbed":"slc",
        "rules": 3,
        "zones": ["salt lake city","salt lake city","Alta town"],
        "strtypes": ["URML","URMM","URML"],
        "pcts": [10,20,20]
    }
    retrofits = {
        "ret_keys":["Wood or Metal Deck Diaphragms Retrofitted","Wood or Metal Deck Diaphragms Retrofitted","Wood or Metal Deck Diaphragms Retrofitted"],
        "ret_vals":["","",""]        
    }

    # rules = {
    #     "testbed":"slc",
    #     "rules": 1,
    #     "zones": ["salt lake city"],
    #     "strtypes": ["URML"],
    #     "pcts": [10]
    # }
    # retrofits = {
    #     "ret_keys":["Wood or Metal Deck Diaphragms Retrofitted"],
    #     "ret_vals":[""]        
    # }


    con = get_connection("rs_data.db")

    df_list = []
    for idx in range(rules['rules']):
        zone = rules['zones'][idx]
        strtype = rules['strtypes'][idx]

        pct = rules['pcts'][idx]
        ret_key = retrofits['ret_keys'][idx]
        ret_val = retrofits['ret_vals'][idx]

        rel = get_buildings(con, strtype, zone)

        df = create_retrofit_strategy_by_rule(idx, rel, pct, ret_key, ret_val)
        df_list.append(df)

    merged_df = merge_create_retrofit_strategy(df_list, result_name)

    # calculate retrofit cost for SLC
    ret_cost_df = rc_slc.get_retrofit_cost(con)
    final_df = rc_slc.compute_retrofit_cost("rc_cost_slc", merged_df, ret_cost_df)

    # create geospatial data of retrofit strategy (with cost)
    create_geo_retrofit_strategy(final_df, result_name)
    con.close()
