import json

import pandas as pd
from pyincore import IncoreClient, Dataset, DataService


def main(input_building_dataset_id, input_retrofit_plan_dataset_id, input_elevation_guide_csv, output_cost_csv,
         output_cost_json, inflation_rate, client):
    # read building data
    building_dataset = Dataset.from_data_service(input_building_dataset_id, DataService(client))
    if building_dataset is not None:
        building_df = building_dataset.get_dataframe_from_shapefile()
    else:
        print("Error: The building dataset is not found.")
        return

    # read retrofit strategy data
    retrofit_strategy_dataset = Dataset.from_data_service(input_retrofit_plan_dataset_id, DataService(client))
    if retrofit_strategy_dataset is not None:
        rf_df = retrofit_strategy_dataset.get_dataframe_from_csv()
    else:
        print("Error: The retrofit strategy dataset is not found.")
        return

    # read elevation guide data
    elevation_guide_df = pd.read_csv(input_elevation_guide_csv)

    # merge building and retrofit plan data using guid as key
    merged_df = pd.merge(building_df, rf_df, on='guid')

    # keep guid bsmt_type, sq_foot, and elevation from building data
    merged_df = merged_df[['guid', 'bsmt_type', 'sq_foot', 'retrofit_value']]

    # make bsmt_type column as integer
    merged_df['bsmt_type'] = merged_df['bsmt_type'].astype(int)

    # map elevation by using bsmt_type and elevation_guide
    bsmt_guide_column = ""
    elevation_column = "Elevation Height (feet)"
    for index, row in merged_df.iterrows():
        bsmt_type = row['bsmt_type']
        sq_foot = row['sq_foot']
        if bsmt_type == 0:
            bsmt_guide_column = "Slab on Grade"
        elif bsmt_type == 1:
            bsmt_guide_column = "Slab on Grade"
        elif bsmt_type == 2:
            bsmt_guide_column = "Slab Separation"
        elif bsmt_type == 3:
            bsmt_guide_column = "Open Foundation"
        elevation_value = row['retrofit_value']
        bsmt_value = elevation_guide_df[elevation_guide_df[elevation_column]
                                        == elevation_value][bsmt_guide_column].values[0]
        merged_df.at[index, 'Retrofit_Cost'] = sq_foot * bsmt_value * inflation_rate

    # fill the blank retrofit_value with NA
    merged_df['retrofit_value'] = merged_df['retrofit_value'].fillna('NA')

    # calculate the total cost
    total_cost = merged_df['Retrofit_Cost'].sum()

    # check the unique basement type
    unique_bsmt_type = merged_df['bsmt_type'].unique()

    # create the total cost for each basement type
    total_cost_by_bsmt = merged_df.groupby('bsmt_type')['Retrofit_Cost'].sum().reset_index()

    # create the total buildings for each basement type
    total_building = merged_df.groupby('bsmt_type')['Retrofit_Cost'].count().reset_index()

    # round the total cost to 2 decimal places
    total_cost = round(total_cost, 2)

    # create the output json
    output_json = {
        "total_cost": total_cost
        # if you need to include following items in output json
        # uncomment the following lines
        # "basement_type": unique_bsmt_type.tolist(),
        # "total_cost_for_each_basement_type": total_cost_by_bsmt.to_dict(orient='records'),
        # "total_buildings_for_each_basement_type": total_building.to_dict(orient='records')
    }

    # save the result to json
    with open(output_cost_json, 'w') as json_file:
        json.dump(output_json, json_file)

    # only keep guid and cost columns
    merged_df = merged_df[['guid', 'Retrofit_Cost']]

    # round the cost to 2 decimal places
    merged_df['Retrofit_Cost'] = merged_df['Retrofit_Cost'].apply(lambda x: round(x, 2))

    # save the result to csv
    merged_df.to_csv(output_cost_csv, index=False)


if __name__ == '__main__':
    client = IncoreClient()

    # input and output parameters
    input_building_dataset_id = "63ff6b135c35c0353d5ed3ac"
    input_retrofit_strategy_dataset_id = "65dcf904c013b927b93bf632"
    input_elevation_guide_csv = "data/elevation_unit_cost_guide.csv"
    output_cost_csv = "data/galveston_cost_output.csv"
    output_cost_json = "data/galveston_cost_output.json"
    inflation_rate = 1.79

    main(input_building_dataset_id, input_retrofit_strategy_dataset_id, input_elevation_guide_csv, output_cost_csv,
         output_cost_json, inflation_rate, client)
    print("Process completed successfully!")
