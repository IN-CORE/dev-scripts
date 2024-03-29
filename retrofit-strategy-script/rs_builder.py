import os
import urllib

import duckdb
import geopandas as gpd
import pandas as pd
import argparse
import json
import requests
from pyincore import IncoreClient, DataService, SpaceService, globals as pyglobals
import signal

import retrofit_cost_slc as rc_slc
import retrofit_cost_galveston as rc_galveston
import retrofit_cost_joplin as rc_joplin

DATA_FILE = "rs_data.db"

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
    "zone_col": "",
    "additional_columns": ["archetype", "gsq_foot"]
}


### get duckdb connection with spatial extension
def get_connection(db_file):
    conn = duckdb.connect(db_file, read_only=False)
    # checking spatial extention and install
    spatial_extension_query = conn.execute(
        "SELECT * FROM duckdb_extensions() WHERE installed IS TRUE AND extension_name = 'spatial';").fetchone()
    if spatial_extension_query is None:
        print("Installing DuckDB spatial extension...")
        conn.execute("INSTALL spatial;")

    # loading spatial extension
    conn.execute("LOAD spatial;")
    return conn


### Get all the buildings in a specific boundary with a specific structure type
def get_buildings(conn, config, struct_typ, bnd_name):

    # adding additional columns to the query
    add_col_str = ""
    for col in config['additional_columns']:
        add_col_str += ", " + col
    
    # adding zone rule to the query. If zone_col is empty, no zone rule is added
    zone_rule_str = f"AND {config['zone_col']}='{bnd_name.upper()}' "
    if config['zone_col'] == "":
        zone_rule_str = ""

    # constructing the sql query
    sql_str = f"SELECT guid, ST_AsText(geom) as geom{add_col_str} FROM {config['bldg_table_name']} " + \
              f"WHERE {config['structure_type_col']}='{struct_typ.upper()}' " + \
              zone_rule_str + ";"

    rel = conn.sql(sql_str)
    print("# of buildings selected:", rel.shape[0])

    return rel


### create a retrofit strategy file from a list of buildings and retrofit strategies
def create_retrofit_strategy_by_rule(idx, rel, percent, retrofit_key, retrofit_val):
    df = rel.to_df()
    # selecting randm buildings with percent
    df_sample = df.sample(frac=percent / 100.0)

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
    rs_csv_name = result_name.replace(" ", "_") + ".csv"
    df[['guid', 'retrofit_key', 'retrofit_value']].to_csv(rs_csv_name, index=False)
    return df, rs_csv_name


def create_geo_retrofit_strategy(df, result_name):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geom']), crs="EPSG:4326")
    gdf.drop(columns=['geom'], inplace=True)
    shapefile_name = result_name.replace(" ", "_") + "_details.shp"
    gdf.to_file(shapefile_name)
    return gdf, shapefile_name


### Parse the retrofit strategy rules
def _parse_param_str(param_str):
    param = json.loads(param_str)
    return param


def _handler(signum, frame):
    print("Forever is over!")
    raise Exception("end of time")


def _get_bearer_token(token_file, service_url):
    with open(token_file, 'r') as f:
        auth = f.read().splitlines()
        # check if token is valid
        userinfo_url = urllib.parse.urljoin(service_url, pyglobals.KEYCLOAK_USERINFO_PATH)
        r = requests.get(userinfo_url, headers={'Authorization': auth[0]})
        if r.status_code != 200:
            return None
    return auth[0]


def store_results(dataservice, spaceservice, source_id, title, local_file, data_type, output_format, spaces):
    output_properties = {"dataType": data_type, "title": title, "description": title, "format": output_format}

    if source_id is not None:
        output_properties["sourceDataset"] = source_id

    # register the handler
    signal.signal(signal.SIGALRM, _handler)

    if output_format == "shapefile":
        files = []
        file_name = os.path.splitext(local_file)[0]
        print("Looking for shapefiles matching on: " + file_name)
        for shp_file in os.listdir("."):
            if shp_file.startswith(file_name):
                files.append(os.path.join(".", shp_file))
    else:
        files = [str(os.path.join(".", local_file))]

    # print("does file exist?")
    # print(path.exists(os.path.join(".", local_file)))

    dataset_id = "temp-id"
    # Use this for testing locally
    save_to_service = True
    if save_to_service:
        response = dataservice.create_dataset(output_properties)
        dataset_id = response['id']
        print("created dataset " + dataset_id)
        # Add file to spaces
        for space in spaces:
            spaceservice.add_to_space_by_name(space, dataset_id)

    print("saving output dataset id")
    output_dataset_id = open(title + "-output_id.txt", "w")
    output_dataset_id.write(dataset_id)
    output_dataset_id.close()

    if save_to_service:
        try:
            # time out after 1 min so tool doesn't get stuck waiting for big files that return responses slowly
            signal.alarm(60)

            print("adding files to dataset")
            dataservice.add_files_to_dataset(dataset_id, files)
        except Exception as exc:
            print(exc)

    return dataset_id


def post_retrofit_summary(service_url, bearer_token, testbed, rs_dataset_id, rules_q, retrofits_q, rs_details_dict,
                          rs_details_layer_id):
    rs_details_summary = {
        **rs_details_dict,
        "rules": rules_q,
        "retrofits": retrofits_q,
        "rsDetailsLayerId": rs_details_layer_id,
    }

    # e.g. https://incore-dev.ncsa.illinois.edu/maestro/slc/datasets/5f9e3e3e3e5f3e3e3e3e3e3e/rsdetails
    response = requests.post(f"{service_url}/maestro/{testbed}/datasets/{rs_dataset_id}/rsdetails",
                             headers={'Authorization': bearer_token},
                             json=rs_details_summary)
    if response.status_code != 200:
        print("Failed to post retrofit strategy summary to the maestro service.")
        print(response.text)
        return None

    return response.status_code


def main(args):
    rules = args.rules
    testbed = rules['testbed']
    if testbed == "slc":
        config = SLC_CONFIG
    elif testbed == "galveston":
        config = GALVESTON_CONFIG
    elif testbed == "joplin":
        config = JOPLIN_CONFIG
    else:
        print("Invalid testbed")
        exit(1)

    retrofits = args.retrofits

    # if no name is provided by the user, construct a name
    strategy_result_name = args.result_name
    if strategy_result_name is None or strategy_result_name == "":
        strategy_result_name = f"Retrofit Strategy {testbed}"
    cost_result_name = f"Retrofit Cost {testbed}"

    # get the buildings from the database
    con = get_connection(DATA_FILE)

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

    # incore:retrofitStrategy
    rs_df, rs_fname = merge_create_retrofit_strategy(df_list, strategy_result_name)

    # calculate retrofit cost and other details
    # incore:retrofitStrategyDetail
    rs_detail_df = pd.DataFrame()
    rs_details_dict = None
    if rules['testbed'] == "slc":
        ret_cost_df = rc_slc.get_retrofit_cost(con)
        rs_detail_df, rs_details_dict = rc_slc.compute_retrofit_cost(cost_result_name, rs_df, ret_cost_df)
    elif rules['testbed'] == "galveston":
        ret_cost_df = rc_galveston.get_retrofit_cost(con)
        rs_detail_df, rs_details_dict = rc_galveston.compute_retrofit_cost(cost_result_name, rs_df, ret_cost_df, 1.79)
    elif rules['testbed'] == "joplin":
        ret_cost_df = rc_joplin.get_retrofit_cost(con)
        rs_detail_df, rs_details_dict = rc_joplin.compute_retrofit_cost(cost_result_name, rs_df, ret_cost_df)
    else:
        print("Invalid testbed")
        exit(1)

    # create geospatial data of retrofit strategy (with cost)
    rs_details_geo_df, rs_details_geo_fname = create_geo_retrofit_strategy(rs_detail_df, strategy_result_name)

    # close the db connection
    con.close()

    # ----------------- Post retrofit strategy to the service -----------------
    token = args.token
    service_url = args.service_url
    spaces = []
    if args.spaces is not None and len(args.spaces) > 0:
        spaces = args.spaces.strip().split(",")

    # Create IN-CORE client
    client = IncoreClient(service_url, token)

    # Data Service
    dataservice = DataService(client)
    spaceservice = SpaceService(client)

    # post retrofit strategy csv to the service
    rs_dataset_id = store_results(dataservice,
                                  spaceservice,
                                  source_id=None,  # Don't join with parent dataset
                                  title=f"{strategy_result_name} Strategy",
                                  local_file=rs_fname,
                                  data_type="incore:retrofitStrategy",
                                  output_format="table",
                                  spaces=spaces)

    # post retrofit strategy detail shapefile to service
    rs_detail_layer_id = store_results(dataservice,
                                       spaceservice,
                                       source_id=None,  # Don't join with parent dataset
                                       title=f"{strategy_result_name} Details",
                                       local_file=rs_details_geo_fname,
                                       data_type="incore:rsDetail",
                                       output_format="shapefile",
                                       spaces=spaces)

    # post retrofit strategy detail json to maestro
    if rs_details_dict is not None:
        bearer_token = _get_bearer_token(args.token, args.service_url)
        status = post_retrofit_summary(service_url, bearer_token, testbed, rs_dataset_id, rules, retrofits,
                                       rs_details_dict,
                                       rs_detail_layer_id)
        print(f"Retrofit strategy summary posted to the maestro service with status code: {status}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generating Retrofit Strategy Dataset and Computing Retrofit Cost')
    parser.add_argument('--rules', dest='rules', type=json.loads, help='Retrofit strategy rules')
    parser.add_argument('--retrofits', dest='retrofits', type=json.loads, help='Retrofit methods and values')
    parser.add_argument('--result_name', dest='result_name', help='Strategy Related Results Name')
    parser.add_argument('--token', dest='token', help='Service token')
    parser.add_argument('--service_url', dest='service_url', help='Service endpoint')
    parser.add_argument('--spaces', dest='spaces', help='Spaces to write to (comma separated)')

    args = parser.parse_args()
    main(args)
