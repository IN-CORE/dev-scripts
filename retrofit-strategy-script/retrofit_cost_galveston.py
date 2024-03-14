import argparse
import json

import pandas as pd

# Global variables
GALVESTON_BLDG_RET_COST_TABLE_NAME = "galveston_bldg_ret_cost"

def get_retrofit_cost(con):
    return con.execute(f"SELECT * FROM {GALVESTON_BLDG_RET_COST_TABLE_NAME}").fetchdf()

def compute_retrofit_cost(result_name, retrofit_strategy_df, input_cost_df, inflation_rate): 

    # set output name
    if result_name is not None:
        output_name = result_name
    else:
        output_name = "retrofit_cost"

    bsmt_type_column = ""
    for index, row in retrofit_strategy_df.iterrows():
        bsmt_type = row['bsmt_type']
        sq_foot = row['sq_foot']
        rasied_elev = row['retrofit_value']
        
        if bsmt_type == '0' or bsmt_type == '1':
            bsmt_type_column = "slab_on_grade"
        elif bsmt_type == '2':
            bsmt_type_column = "slab_separation"
        elif bsmt_type == '3':
            bsmt_type_column = "open_foundation"
        else:
            print("Invalid bsmt_type value and can't calculate retrofit cost")
            retrofit_strategy_df.at[index, 'retrofit_cost'] = -1
            continue

        unit_cost = input_cost_df[input_cost_df['elev_ft'] == rasied_elev][bsmt_type_column].values[0]
        retrofit_cost = sq_foot * unit_cost * inflation_rate

        retrofit_strategy_df.at[index, 'retrofit_cost'] = retrofit_cost

    total = {}
    by_rule = {}


    # fill na values with -1 for retrofit cost
    retrofit_strategy_df['retrofit_cost'] = retrofit_strategy_df['retrofit_cost'].fillna(-1)
    retrofit_strategy_df['retrofit_cost'] = retrofit_strategy_df['retrofit_cost'].round(2)

    # total number of building
    total['num_bldg'] = retrofit_strategy_df.shape[0]

    # number of buildings by rule
    count_by_rule = retrofit_strategy_df[['guid','rule']].groupby('rule').count()
    count_by_rule_dict = count_by_rule.to_dict()
    for k,v in count_by_rule_dict['guid'].items():
        by_rule[k] = {"num_bldg": v}

    # select rows with positive retrofit cost
    rs_postive_df = retrofit_strategy_df[retrofit_strategy_df['retrofit_cost'] > 0]

    # number of buildings with negative retrofit cost
    total['num_bldg_no_cost'] = total['num_bldg'] - rs_postive_df.shape[0]

    # number of buildings (positive) by rule
    count_postive_by_rule = rs_postive_df[['guid','rule']].groupby('rule').count()
    count_postive_by_rule_dict = count_postive_by_rule.to_dict()
    for k in by_rule.keys():
        n = 0
        if k in count_postive_by_rule_dict['guid']:
            n = count_postive_by_rule_dict['guid'][k]
        by_rule[k]["num_bldg_no_cost"] = by_rule[k]['num_bldg'] - n

    # compute total retrofit cost
    total_ret_cost = rs_postive_df['retrofit_cost'].sum()
    total['cost'] = total_ret_cost

    # compute total retrofit cost by rule
    total_ret_cost_by_rule = rs_postive_df[['rule','retrofit_cost']].groupby('rule').sum()
    total_ret_cost_by_rule_dict = total_ret_cost_by_rule.to_dict()
    for k in by_rule.keys():
        c = 0
        if k in total_ret_cost_by_rule_dict['retrofit_cost']:
            c = total_ret_cost_by_rule_dict['retrofit_cost'][k]
        by_rule[k]["cost"] = c

    # create json output
    # {
    #     "total": {
    #         "num_bldg": 1234,
    #         "num_bldg_no_cost": 1234,
    #         "cost": 1234,
    #     },
    #     "by_rule":{
    #         0: {
    #             "num_bldg": 123,
    #             "num_bldg_no_cost": 123,
    #             "cost": 123
    #         },
    #         1:  {
    #             "num_bldg": 123,
    #             "num_bldg_no_cost": 123,
    #             "cost": 123
    #         }
    #     }
    # }
    output_json = {
        "total": total,
        "by_rule": by_rule
    }

    # save the output cost json
    # the output json name is hardcoded as "retrofit_cost.json"
    with open(output_name + ".json", 'w') as f:
        json.dump(output_json, f, indent=4)

    return retrofit_strategy_df

