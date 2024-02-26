#!/usr/bin/env python3
import json
import pandas as pd


def main(input_cost_csv, output_cost_csv, output_cost_json, inflation_rate):
    # read input cost csv
    cost_df = pd.read_csv(input_cost_csv)

    # keep only necessary columns
    cost_df = cost_df[['guid', 'struct_typ', 'Retrofit_Cost']]

    # remove the rows with missing retrofit cost
    cost_df = cost_df.dropna(subset=['Retrofit_Cost'])

    # convert retrofit cost to float
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'].astype(float)

    # apply inflation by multiplying the retrofit cost by inflation rate
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'] * inflation_rate

    # round the retrofit cost to 2 decimal places
    cost_df['Retrofit_Cost'] = cost_df['Retrofit_Cost'].round(2)

    # check the unique structure types
    struct_types = cost_df['struct_typ'].unique()

    # create the total cost value
    total_cost = cost_df['Retrofit_Cost'].sum()

    # create total cost by structure type
    struct_cost = cost_df.groupby('struct_typ')['Retrofit_Cost'].sum().reset_index()

    # create total number of rows by structure type
    struct_count = cost_df.groupby('struct_typ')['Retrofit_Cost'].count().reset_index()

    # create json output
    output_json = {
        "total_cost": total_cost,
        "structure_types": struct_types.tolist(),
        "total_cost_by_struct_type": struct_cost.to_dict(orient='records'),
        "total_count_by_struct_type": struct_count.to_dict(orient='records')
    }

    # save the output cost json
    with open(output_cost_json, 'w') as f:
        json.dump(output_json, f, indent=4)

    # drop struct_typ column
    cost_df = cost_df.drop(columns=['struct_typ'])

    # save the output cost csv
    cost_df.to_csv(output_cost_csv, index=False)


if __name__ == '__main__':
    # result file
    input_cost_csv = "data/Salt_Lake_City_Build_W_Cost.csv"
    output_cost_csv = "data/Salt_Lake_City_Build_W_Cost_output.csv"
    output_cost_json = "data/Salt_Lake_City_Build_W_Cost_output.json"
    inflation_rate = 1.79

    main(input_cost_csv, output_cost_csv, output_cost_json, inflation_rate)
    print("Process completed successfully!")
