#!/usr/bin/env python3
import argparse
import json
import pandas as pd

from pyincore import Dataset, AnalysisUtil
from pyincore import IncoreClient
from pyincore.dataservice import DataService


def main():
    # IN-CORE token (optional)
    token = args.token

    # IN-CORE Service URL
    service_url = args.service_url

    # Result name (optional)
    result_name = args.result_name

    # Retrofit Strategy dataset ID
    retrofit_strategy_id = args.retrofit_strategy_id

    # Input cost CSV file
    input_cost_csv = args.input_cost_csv

    # Inflation rate
    inflation_rate = float(args.inflation_rate)

    # Create IN-CORE client
    client = IncoreClient(service_url, token)

    # set output name
    if result_name is not None:
        output_name = result_name + "_retrofit_cost"
    else:
        output_name = "retrofit_cost"

    # download the retrofit cost csv from the API
    retrofit_strategy_dataset = Dataset.from_data_service(retrofit_strategy_id, DataService(client))

    if retrofit_strategy_dataset is not None:
        rf_df = retrofit_strategy_dataset.get_dataframe_from_csv()
    else:
        print("Error: The retrofit strategy dataset is not found.")
        return

    # read input cost csv
    cost_df = pd.read_csv(input_cost_csv)

    # merge rf_df and cost_df using guid column
    cost_df = cost_df.merge(rf_df, on='guid', how='right')

    # keep only necessary columns
    # if the column names are different, this will make an error
    try:
        cost_df = cost_df[['guid', 'struct_typ', 'retrofit_key', 'Retrofit_Cost']]
    except KeyError:
        print("Error: The input cost csv does not have the necessary columns.")
        return

    # fill the balnk retrofit cost with NA
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'].fillna('NA')

    # convert retrofit cost to float
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'].astype(float)

    # apply inflation by multiplying the retrofit cost by inflation rate
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'] * inflation_rate

    # round the retrofit cost to 2 decimal places
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'].round(2)

    # check the unique structure types
    struct_types = cost_df['struct_typ'].unique()

    # check the unique retrofit keys
    retrofit_keys = cost_df['retrofit_key'].unique()

    # create the total cost value
    total_cost = cost_df['Retrofit_Cost'].sum()

    # create total cost by structure type
    struct_cost = cost_df.groupby('struct_typ')['Retrofit_Cost'].sum().reset_index()

    # create total cost by retrofit key
    retrofit_cost = cost_df.groupby('retrofit_key')['Retrofit_Cost'].sum().reset_index()

    # create total number of rows by structure type
    struct_count = cost_df.groupby('struct_typ')['Retrofit_Cost'].count().reset_index()

    # create total number of rows by retrofit key
    retrofit_count = cost_df.groupby('retrofit_key')['Retrofit_Cost'].count().reset_index()

    # create json output
    output_json = {
        "total_cost": total_cost
        # if you need to include following items in output json
        # uncomment the following lines
        # "structure_types": struct_types.tolist(),
        # "total_cost_by_building_type": struct_cost.to_dict(orient='records'),
        # "total_count_by_building_type": struct_count.to_dict(orient='records'),
        # "retrofit_keys": retrofit_keys.tolist(),
        # "total_cost_by_retrofit_key": retrofit_cost.to_dict(orient='records'),
        # "total_count_by_retrofit_key": retrofit_count.to_dict(orient='records')
    }

    # save the output cost json
    # the output json name is hardcoded as "retrofit_cost.json"
    with open(output_name + ".json", 'w') as f:
        json.dump(output_json, f, indent=4)

    # keep only necessary columns
    cost_df = cost_df[['guid', 'Retrofit_Cost']]

    # save the output cost csv
    # the output csv name is hardcoded as "retrofit_cost.csv"
    cost_df.to_csv(output_name + ".csv", index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate retrofit cost for SLC.')
    parser.add_argument('--token', dest='token', help='Service token')
    parser.add_argument('--result_name', dest='result_name', help='Result name')
    parser.add_argument('--service_url', dest='service_url', help='Service URL')
    parser.add_argument('--retrofit_strategy_id', dest='retrofit_strategy_id', help='Retrofit Strategy dataset ID')
    parser.add_argument('--input_cost_csv', dest='input_cost_csv', help='Input cost CSV file')
    parser.add_argument('--inflation_rate', dest='inflation_rate', help='Inflation rate')

    args = parser.parse_args()
    main()

    # to run the script, use the following command
    # python slc_retrofit_cost.py --token <your_token> --result_name SLC --service_url https://incore-dev.ncsa.illinois.edu --retrofit_strategy_id 65d5206b8215870f805d6001 --input_cost_csv data/Salt_Lake_City_Build_W_Cost.csv --inflation_rate 1



