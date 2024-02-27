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

    # drop the rows with null retrofit cost
    merged_df = merged_df.dropna(subset=['Retrofit_Cost'])

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
        "total_cost": total_cost,
        "basement_type": unique_bsmt_type.tolist(),
        "total_cost_for_each_basement_type": total_cost_by_bsmt.to_dict(orient='records'),
        "total_buildings_for_each_basement_type": total_building.to_dict(orient='records')
    }

    # save the result to json
    with open(output_cost_json, 'w') as json_file:
        json_file.write(str(output_json))

    # only keep guid and cost columns
    merged_df = merged_df[['guid', 'Retrofit_Cost']]

    # round the cost to 2 decimal places
    merged_df['Retrofit_Cost'] = merged_df['Retrofit_Cost'].apply(lambda x: round(x, 2))

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
