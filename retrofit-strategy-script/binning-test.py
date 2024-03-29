import os
import urllib

import duckdb
import geopandas as gpd
import pandas as pd

from pyincore import IncoreClient, DataService, SpaceService, globals as pyglobals


import numpy as np

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



def main():

    con = get_connection(DATA_FILE)
    config = SLC_CONFIG
    sql_str = f"SELECT guid, ST_AsText(geom) as geom FROM {config['bldg_table_name']};"

    rel = con.sql(sql_str)
    df = rel.to_df()
    # shuffle the buildings
    df = df.sample(frac=1).reset_index(drop=True)

    # # test keep only 5 buildings
    # df = df[:5]

    # # test keep 1 building
    # df = df[:1]

    # test keep 0 buildings
    df = pd.DataFrame()

    percents = [20, 30, 30]
    # percents = [0, 100]
    # percents = [100, 0, 0, 0]
    # percents = [0, 100, 0, 0]
    # percents = [0, 0, 0, 0, 0]
    # percents = [1, 2, 2, 90]
    # percents = [1, 90, 2, 1]
    # percents = [0, 49, 51, 0]
    # percents = [0, 51, 49, 0]

    total = len(df)
    cumulative_percents = np.cumsum([0] + percents)
    bin_edges = [round(pct / 100 * total) for pct in cumulative_percents]

    # preventive bin edges can't be larger than the total number of buildings
    if bin_edges[-1] > total:
        bin_edges[-1] = total

    # Function to use a sliding window of size 2 to find non-overlapping bins
    def _find_effective_bins():
        labels=range(1, len(percents) + 1)
        effective_bins = {}
        selected_labels = []
        for i in range(len(bin_edges) - 1):
            if bin_edges[i] != bin_edges[i + 1]:
                effective_bins[i] = (bin_edges[i], bin_edges[i + 1])
        # For each non-overlapping bin, select the corresponding label.
        for idx in effective_bins:
            selected_labels.append(labels[idx])

        return selected_labels

    # If one segment is 100%, directly assign values without binning
    if 100 in percents:
        raise ValueError("handle 100%")
    # if all percents are 0, return an empty DataFrame
    elif all(p == 0 for p in percents):
        raise ValueError("handle 0%")

    df['segment_id'] = pd.cut(df.index,
                              bins=bin_edges,
                              labels=_find_effective_bins(),
                              include_lowest=False, right=False, duplicates='drop')

    building_counts = df.groupby('segment_id', observed=False).size()
    for count in building_counts.items():
        print(f"# of buildings sampled: {count[1]} / {df.shape[0]}")


if __name__ == '__main__':

    main()
