import pandas as pd

def main(input_building_csv, retrofit_plan_csv, input_elevation_guide_csv, output_cost_csv,
         output_cost_json, inflation_rate):
    # read building data
    building_df = pd.read_csv(input_building_csv)

    # read retrofit plan data
    retrofit_plan_df = pd.read_csv(retrofit_plan_csv)

    # read elevation guide data
    elevation_guide_df = pd.read_csv(input_elevation_guide_csv)

    # merge building and retrofit plan data using guid as key
    merged_df = pd.merge(building_df, retrofit_plan_df, on='guid')

    # keep guid bsmt_type, sq_foot, and elevation from building data
    merged_df = merged_df[['guid', 'bsmt_type', 'sq_foot', 'retrofit_value']]

    # map elevation by using bsmt_type and elevation_guide
    bsmt_guide_column = ""
    elevation_column = "Elevation Height (feet)"
    for index, row in merged_df.iterrows():
        bsmt_type = row['bsmt_type']
        sq_foot = row['sq_foot']
        if bsmt_type == 0:
            bsmt_guide_column = "Type 0"
        elif bsmt_type == 1:
            bsmt_guide_column = "Type 1"
        elif bsmt_type == 2:
            bsmt_guide_column = "Type 2"
        elif bsmt_type == 3:
            bsmt_guide_column = "Type 3"
        elevation_value = row['retrofit_value']
        bsmt_value = elevation_guide_df[elevation_guide_df[elevation_column] == elevation_value][bsmt_guide_column].values[0]
        merged_df.at[index, 'cost'] = sq_foot * bsmt_value * inflation_rate

    # calculate the total cost
    total_cost = merged_df['cost'].sum()

    # check the unique basement type
    unique_bsmt_type = building_df['bsmt_type'].unique()

    # create the total cost for each basement type
    total_cost_by_bsmt = []
    for bsmt_type in unique_bsmt_type:
        total_cost_by_bsmt.append(merged_df[merged_df['bsmt_type'] == bsmt_type]['cost'].sum())

    # create the total buildings for each basement type
    total_building = []
    for bsmt_type in unique_bsmt_type:
        total_building.append(merged_df[merged_df['bsmt_type'] == bsmt_type]['guid'].count())

    # create the average cost for each basement type
    average_cost = []
    for i in range(len(unique_bsmt_type)):
        average_cost.append(total_cost_by_bsmt[i] / total_building[i])

    # round the total cost to 2 decimal places
    total_cost = round(total_cost, 2)

    # round the total cost for each basement type to 2 decimal places
    total_cost_by_bsmt = [round(x, 2) for x in total_cost_by_bsmt]

    # round the average cost to 2 decimal places
    average_cost = [round(x, 2) for x in average_cost]

    # create the json including total cost, basement type, total cost for each basement type, total buildings for each basement type, and average cost for each basement type
    cost_json = { "total_cost": total_cost, "basement_type": unique_bsmt_type.tolist(), "total_cost_for_each_basement_type": total_cost_by_bsmt, "total_buildings_for_each_basement_type": total_building, "average_cost_for_each_basement_type": average_cost }

    # save the result to json
    with open(output_cost_json, 'w') as json_file:
        json_file.write(str(cost_json))

    # only keep guid and cost columns
    merged_df = merged_df[['guid', 'cost']]

    # round the cost to 2 decimal places
    merged_df['cost'] = merged_df['cost'].apply(lambda x: round(x, 2))

    # save the result to csv
    merged_df.to_csv(output_cost_csv, index=False)


if __name__ == '__main__':
    # result file
    input_building_csv = "data/galveston_bldg_island2.csv"
    retrofit_plan_csv = "data/galveston_retrofit_plan.csv"
    input_elevation_guide_csv = "data/elevation_unit_cost_guide.csv"
    output_cost_csv = "data/galveston_cost_output.csv"
    output_cost_json = "data/galveston_cost_output.json"
    inflation_rate = 1.79

    main(input_building_csv, retrofit_plan_csv, input_elevation_guide_csv, output_cost_csv,
         output_cost_json, inflation_rate)
    print("Process completed successfully!")