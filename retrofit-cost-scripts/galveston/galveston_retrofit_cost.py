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

    # map bsmnt_type to elevation
    merged_df['elevation'] = merged_df['bsmt_type'].map(elevation_guide_df.set_index('bsmt_type')['elevation'])


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