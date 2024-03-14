import duckdb
import geopandas as gpd
import pandas as pd
import argparse
import json
import retrofit_cost_slc as rc_slc
import retrofit_cost_galveston as rc_galveston

SLC_CONFIG = {
    "bldg_table_name": "slc",
    "structure_type_col": "struct_typ",
    "zone_col": "NAME",
    "additional_columns": []
}

GALVESTON_CONFIG = {
    "bldg_table_name": "galveston",
    "structure_type_col": "arch_wind",
    "zone_col": "fld_zone2",
    "additional_columns": ["bsmt_type", "sq_foot"]
}

JOPLIN_CONFIG = {
    "bldg_table_name": "joplin",
    "structure_type_col": "archetype",
    "zone_col": "name"
}

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
def get_buildings(conn, config, struct_typ, bnd_name):
    add_col_str = ""
    for col in config['additional_columns']:
        add_col_str += ", " + col

    sql_str = f"SELECT guid, ST_AsText(geom) as geom{add_col_str} FROM {config['bldg_table_name']} " + \
            f"WHERE {config['structure_type_col']}='{struct_typ.upper()}' " + \
            f"AND {config['zone_col']}='{bnd_name.upper()}';"
    print(sql_str)
    rel = conn.sql(sql_str)
    print("# of buildings selected:", rel.shape[0])

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

    ### testing with 1 rule for Galveston
    # rules = {
    #     "testbed":"galveston",
    #     "rules": 1,
    #     "zones": ["0.2P"],
    #     "strtypes": ["1"],
    #     "pcts": [5]
    # }
    # retrofits = {
    #     "ret_keys":["elevation"],
    #     "ret_vals":[5]        
    # }

    ### testing with 1 rule for Galveston
    rules = {
        "testbed":"galveston",
        "rules": 3,
        "zones": ["1P", "1P", "0.2P"],
        "strtypes": ["1", "2", "1"],
        "pcts": [1,1,1]
    }
    retrofits = {
        "ret_keys":["elevation","elevation","elevation"],
        "ret_vals":[5, 10, 5]        
    }

    #### testing with 3 rules for SLC
    # rules = {
    #     "testbed":"slc",
    #     "rules": 3,
    #     "zones": ["COUNCIL DISTRICT 1","COUNCIL DISTRICT 2","COUNCIL DISTRICT 3"],
    #     "strtypes": ["URML","URMM","URML"],
    #     "pcts": [10,20,20]
    # }
    # retrofits = {
    #     "ret_keys":["Wood or Metal Deck Diaphragms Retrofitted","Wood or Metal Deck Diaphragms Retrofitted","Wood or Metal Deck Diaphragms Retrofitted"],
    #     "ret_vals":["","",""]        
    # }

    #### testing with 1 rule for SLC
    # rules = {
    #     "testbed":"slc",
    #     "rules": 1,
    #     "zones": ["COUNCIL DISTRICT 2"],
    #     "strtypes": ["URML"],
    #     "pcts": [10]
    # }
    # retrofits = {
    #     "ret_keys":["Wood or Metal Deck Diaphragms Retrofitted"],
    #     "ret_vals":[""]        
    # }

    result_name = "retrofit_strategy_galveston"

    con = get_connection("rs_data.db")

    config = {}
    if rules['testbed'] == "slc":
        config = SLC_CONFIG
    elif rules['testbed'] == "galveston":
        config = GALVESTON_CONFIG
    elif rules['testbed'] == "joplin":
        config = JOPLIN_CONFIG
    else:
        print("Invalid testbed")
        exit(1)

    df_list = []
    for idx in range(rules['rules']):
        zone = rules['zones'][idx]
        strtype = rules['strtypes'][idx]

        pct = rules['pcts'][idx]
        ret_key = retrofits['ret_keys'][idx]
        ret_val = retrofits['ret_vals'][idx]

        rel = get_buildings(con, config, strtype, zone)

        df = create_retrofit_strategy_by_rule(idx, rel, pct, ret_key, ret_val)
        if df.shape[0] > 0:
            df_list.append(df)

    merged_df = merge_create_retrofit_strategy(df_list, result_name)

    # # calculate retrofit cost
    if rules['testbed'] == "slc":
        ret_cost_df = rc_slc.get_retrofit_cost(con)
        final_df = rc_slc.compute_retrofit_cost("rc_cost_slc", merged_df, ret_cost_df)    
    elif rules['testbed'] == "galveston":
        ret_cost_df = rc_galveston.get_retrofit_cost(con)
        final_df = rc_galveston.compute_retrofit_cost("rc_cost_galveston", merged_df, ret_cost_df, 1.79)  
    elif rules['testbed'] == "joplin":
        pass
    else:
        print("Invalid testbed")
        exit(1)

    print(final_df.columns)
    # create geospatial data of retrofit strategy (with cost)
    create_geo_retrofit_strategy(final_df, result_name)
    con.close()
