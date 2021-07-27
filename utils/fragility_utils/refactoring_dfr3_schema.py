#!/usr/bin/env python
# coding: utf-8
import json
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from num2words import num2words
import traceback
import logging


def convert_standard_fragility_set(curve_set):
    new_curve_set = curve_set.copy()

    demand_name, fullName = _convert_demand_type_w_space(curve_set["demandTypes"][0])
    new_curve_set["fragilityCurveParameters"] = [{
        "name": demand_name,
        "unit": curve_set["demandUnits"][0],
        "description": fullName + " value from hazard service",
    }]

    if fullName is not None:
        new_curve_set["fragilityCurveParameters"][0]["fullName"] = fullName

    new_curve_set["fragilityCurves"] = []
    for i, curve in enumerate(curve_set["fragilityCurves"]):
        new_curve = {}
        new_curve["description"] = "legacy - StandardFragilityCurve - " + curve["description"]
        new_curve["className"] = curve["className"].replace("StandardFragilityCurve", "FragilityCurveRefactored")
        new_curve["returnType"] = {"type": "Limit State",
                                   "unit": "",
                                   "description": _ls_renaming(i)}

        if curve.get("alphaType") == "median":
            new_curve["rules"] = [{
                "condition": [_add_demandtype_condition(demand_name)],
                "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ") - math.log({0}))/({1}))".format(
                    curve["alpha"], curve["beta"])}]
        elif curve.get("alphaType") == "lambda":
            new_curve["rules"] = [{
                "condition": [_add_demandtype_condition(demand_name)],
                "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ") - ({0}))/({1}))".format(
                    curve["alpha"], curve["beta"])}]
        else:
            print("cannot convert this fragility curve set: " + str(curve_set["_id"]))
            return {}

        new_curve_set["fragilityCurves"].append(new_curve)

    return new_curve_set


def convert_period_standard_fragility_set(curve_set):
    new_curve_set = curve_set.copy()

    demand_name, fullName = _convert_demand_type_w_space(curve_set["demandTypes"][0])

    # default to the first curve calcuation
    common_period_expression = _building_period_expression(curve_set["fragilityCurves"][0])
    new_curve_set["fragilityCurveParameters"] = [
        {
            "name": demand_name,
            "unit": curve_set["demandUnits"][0],
            "description": fullName + " value from hazard service",
        },
        {
            "name": "num_stories",
            "unit": "",
            "description": "number of stories in building inventory",
            "expression": "1"
        },
        # default
        {
            "name": "period",
            "unit": "",
            "description": "default building period",
            "expression": common_period_expression
        }
    ]

    if fullName is not None:
        new_curve_set["fragilityCurveParameters"][0]["fullName"] = fullName

    new_curve_set["fragilityCurves"] = []
    for i, curve in enumerate(curve_set["fragilityCurves"]):
        new_curve = {}

        new_curve["description"] = "legacy - PeriodStandardFragilityCurve - " + curve["description"]

        # calculate building period and put it in fragilityCurveParameters overwrite
        expression = _building_period_expression(curve)
        if expression != common_period_expression:
            new_curve["fragilityCurveParameters"] = [
                {
                    "name": "period",
                    "unit": "",
                    "description": "Building period calculation",
                    "expression": expression
                }]

        # the rest
        new_curve["className"] = curve["className"].replace("PeriodStandardFragilityCurve", "FragilityCurveRefactored")
        new_curve["returnType"] = {"type": "Limit State",
                                   "unit": "",
                                   "description": _ls_renaming(i)}

        if curve.get("alphaType") == "median":
            new_curve["rules"] = [{
                "condition": [_add_demandtype_condition(demand_name)],
                "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ") - math.log({0}))/({1}))".format(
                    curve["alpha"], curve["beta"])}]
        elif curve.get("alphaType") == "lambda":
            new_curve["rules"] = [
                {
                    "condition": [_add_demandtype_condition(demand_name)],
                    "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ") - ({0}))/({1}))".format(
                        curve["alpha"], curve["beta"])}]
        else:
            print("cannot convert this fragility curve set: " + str(curve_set["_id"]))
            return {}

        new_curve_set["fragilityCurves"].append(new_curve)

    return new_curve_set


def convert_period_building_fragility_curve(curve_set):
    new_curve_set = curve_set.copy()

    demand_name, fullName = _convert_demand_type_w_space(curve_set["demandTypes"][0])

    common_period_expression = _building_period_expression(curve_set["fragilityCurves"][0])
    new_curve_set["fragilityCurveParameters"] = [
        {
            "name": demand_name,
            "unit": curve_set["demandUnits"][0],
            "description": fullName + " value from hazard service",
        },
        {
            "name": "num_stories",
            "unit": "",
            "description": "number of stories in building inventory",
            "expression": "1"
        },
        # default
        {
            "name": "cutoff_period",
            "unit": "",
            "description": "constant",
            "expression": "0.87"
        },
        {
            "name": "period",
            "unit": "",
            "description": "default building period",
            "expression": common_period_expression
        }
    ]

    if fullName is not None:
        new_curve_set["fragilityCurveParameters"][0]["fullName"] = fullName

    new_curve_set["fragilityCurves"] = []
    for i, curve in enumerate(curve_set["fragilityCurves"]):
        new_curve = {}

        new_curve["description"] = "legacy - PeriodBuildingFragilityCurve - " + curve["description"]

        # calculate building period and put it in fragilityCurveParameters overwrite
        expression = _building_period_expression(curve)
        if expression != common_period_expression:
            new_curve["fragilityCurveParameters"] = [
                {
                    "name": "period",
                    "unit": "",
                    "description": "default building period",
                    "expression": expression
                }
            ]

        # the rest
        new_curve["className"] = curve["className"].replace("PeriodBuildingFragilityCurve", "FragilityCurveRefactored")
        new_curve["returnType"] = {"type": "Limit State",
                                   "unit": "",
                                   "description": _ls_renaming(i)}
        new_curve["rules"] = [
            {
                "condition": ["period < cutoff_period",
                              _add_demandtype_condition(demand_name)
                              ],
                "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ")-(cutoff_period * ({1}) + ({0}))) "
                                                                                "/ (({2}) + ({3}) * cutoff_period) + "
                                                                                "(cutoff_period - period) * (math.log(".format(
                    curve["fsParam0"], curve["fsParam1"], curve["fsParam2"], curve["fsParam3"])
                              + demand_name + ") - ({0}))/({1}))".format(curve["fsParam4"], curve["fsParam5"])
            },
            {
                "condition": [
                    "period >= cutoff_period",
                    _add_demandtype_condition(demand_name)
                ],
                "expression": "scipy.stats.norm.cdf((math.log(" + demand_name +
                              ") - (({0}) + ({1}) * period)) / (({2}) + ({3}) * period))".format(curve["fsParam0"],
                                                                                                 curve["fsParam1"],
                                                                                                 curve["fsParam2"],
                                                                                                 curve["fsParam3"])
            }
        ]

        new_curve_set["fragilityCurves"].append(new_curve)

    return new_curve_set


def convert_conditional_standard_fragility_set(curve_set):
    new_curve_set = curve_set.copy()

    demand_name, fullName = _convert_demand_type_w_space(curve_set["demandTypes"][0])
    new_curve_set["fragilityCurveParameters"] = [{
        "name": demand_name,
        "unit": curve_set["demandUnits"][0],
        "description": fullName + " value from hazard service",
    }]
    if fullName is not None:
        new_curve_set["fragilityCurveParameters"][0]["fullName"] = fullName

    new_curve_set["fragilityCurves"] = []
    for i, curve in enumerate(curve_set["fragilityCurves"]):
        new_curve = {}
        new_curve["description"] = "legacy - ConditionalStandardFragilityCurve - " + curve["description"]
        new_curve["className"] = curve["className"].replace("ConditionalStandardFragilityCurve",
                                                            "FragilityCurveRefactored")
        new_curve["returnType"] = {"type": "Limit State",
                                   "unit": "",
                                   "description": _ls_renaming(i)}
        rules = []
        if curve.get("alphaType") == "median":
            for index in curve["rules"].keys():
                condition = [_marshal_string(r, demand_name) for r in
                             curve["rules"][index]]
                condition.append(_add_demandtype_condition(demand_name))
                rules.append({
                    "condition": condition,
                    "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ") - math.log({0}))/({1}))".format(
                        curve["alpha"][int(index)], curve["beta"][int(index)])
                })
        elif curve.get("alphaType") == "lambda":
            for index in curve["rules"].keys():
                condition = [_marshal_string(r, demand_name) for r in curve["rules"][index]]
                condition.append(_add_demandtype_condition(demand_name))
                rules.append({
                    "condition": condition,
                    "expression": "scipy.stats.norm.cdf((math.log(" + demand_name + ") - ({0}))/({1}))".format(
                        curve["alpha"][
                            int(index)],
                        curve["beta"][int(index)])})
        else:
            print("cannot convert this fragility curve set: " + str(curve_set["_id"]))
            return {}

        new_curve["rules"] = rules

        new_curve_set["fragilityCurves"].append(new_curve)

    return new_curve_set


def convert_custom_expression_fragility_curve(curve_set):
    new_curve_set = {}
    if 'inventoryType' in curve_set and curve_set["inventoryType"] == "buried_pipeline":
        new_curve_set = curve_set.copy()

        demand_name, fullName = _convert_demand_type_w_space(curve_set["demandTypes"][0])
        new_curve_set["fragilityCurveParameters"] = [{
            "name": demand_name,
            "unit": curve_set["demandUnits"][0],
            "description": fullName + " value from hazard service",
        }]

        if fullName is not None:
            new_curve_set["fragilityCurveParameters"][0]["fullName"] = fullName

        new_curve_set["fragilityCurves"] = []
        for i, curve in enumerate(curve_set["fragilityCurves"]):
            new_curve = {}
            new_curve["description"] = "legacy - CustomExpressionFragilityCurve - " + curve["description"]
            new_curve["className"] = curve["className"].replace("CustomExpressionFragilityCurve",
                                                                "FragilityCurveRefactored")
            new_curve["returnType"] = {"type": "Repair Rate",
                                       "unit": curve["description"],
                                       "description": _ls_renaming(i)}

            new_curve["rules"] = [{
                    "condition": [_add_demandtype_condition(demand_name)],
                    "expression": curve["expression"]
                        .replace('x', demand_name)
                        .replace('LogTen', 'math.log10')
                        .replace('[', '(')
                        .replace(']', ')')
                        .replace('^', '**')
            }]

            if 'y' in curve["expression"]:
                new_curve["rules"][0]["expression"] = new_curve["rules"][0]["expression"].replace('y', 'diameter')
                new_curve_set["fragilityCurveParameters"].append({
                    "name": "diameter",
                    "unit": "ft",
                    "description": "diameter of the pipeline",
                    "expression": 6
                })

            new_curve_set["fragilityCurves"].append(new_curve)
    else:
        print("custom expression fragility curve: " + str(curve_set["_id"]) + " needs manual conversion!")

    return new_curve_set


def convert_parametric_fragility_curve(curve_set):
    new_curve_set = curve_set.copy()

    demand_name, fullName = _convert_demand_type_w_space(curve_set["demandTypes"][0])

    new_curve_set["fragilityCurveParameters"] = []
    recorded_parameter_name = []

    new_curve_set["fragilityCurves"] = []
    for i, curve in enumerate(curve_set["fragilityCurves"]):
        new_curve = {}
        new_curve["description"] = "legacy - ParametricFragilityCurve - " + curve["description"]
        new_curve["className"] = curve["className"].replace("ParametricFragilityCurve", "FragilityCurveRefactored")
        new_curve["returnType"] = {"type": "Limit State",
                                   "unit": "",
                                   "description": _ls_renaming(i)}

        if curve.get("curveType").lower() == "logit":
            cumulate_term = ""  # X*theta'
            for index, parameter_set in enumerate(curve["parameters"]):
                name = parameter_set["name"]
                unit = parameter_set["unit"]
                coefficient = parameter_set["coefficient"]
                default = parameter_set["interceptTermDefault"]

                # record parameters in the fragility curve parameters
                if name not in recorded_parameter_name and name.lower() != "constant":
                    if name.lower() == "demand":
                        new_curve_set["fragilityCurveParameters"].append({
                            "name": demand_name,
                            "unit": unit,
                            "description": name,
                        })
                        if fullName is not None:
                            new_curve_set["fragilityCurveParameters"][0]["fullName"] = fullName
                    else:
                        new_curve_set["fragilityCurveParameters"].append({
                            "name": name,
                            "unit": unit,
                            "description": name,
                            "expression": str(default)
                        })
                    recorded_parameter_name.append(name)

                # convert to the expression string
                if index > 0:
                    cumulate_term += " + "
                if name.lower() == "demand":
                    cumulate_term += "math.log(" + demand_name + ") * (" + str(coefficient) + ")"
                elif name.lower() == "constant":
                    cumulate_term += "(" + str(coefficient) + ")"
                else:
                    cumulate_term += name + " * (" + str(coefficient) + ")"

            probability = "math.exp(" + cumulate_term + ") / (1 + math.exp(" + cumulate_term + "))"
            new_curve["rules"] = [{
                "condition": [_add_demandtype_condition(demand_name)],
                "expression": probability
            }]

        else:
            print("cannot convert this fragility curve set: " + str(curve_set["_id"]))
            return {}

        new_curve_set["fragilityCurves"].append(new_curve)

    return new_curve_set


def _marshal_string(string, demand_type):
    string = string.replace("demand", demand_type).replace("EQ", "==").replace("EQUALS", "==").replace("NEQUALS",
                                                                                                       "!=").replace(
        "GT", ">").replace("GE", ">=").replace("LT", "<").replace("EQ", "==")

    return string


def _convert_demand_type_w_space(demand_type):
    # for example 0.2 sec Sa, that varialbe cannot start with number, nor can it contain space
    fullName = demand_type
    item_list = []
    for item in demand_type.split(" "):
        if re.match(r'^\d', item) is None:
            item_list.append(item)
        else:
            # when there is number, need to record the fullName
            # e.g. "name": "point_two_sec_SA",
            #       "fullName": "0.2 sec Sa",
            item_list.append(num2words(item).replace(" ", "_"))
            fullName = demand_type

    demand_name = "_".join(item_list)

    return demand_name, fullName


def _building_period_expression(curve):
    # calculate building period and put it in fragilityCurveParameters overwrite
    if curve["periodEqnType"] == 1:
        expression = str(curve["periodParam0"])
    elif curve["periodEqnType"] == 2:
        expression = "num_stories * (" + str(curve["periodParam0"]) + ")"
    elif curve["periodEqnType"] == 3:
        # self.period_param1 * math.pow(self.period_param0 * num_stories, self.period_param2)
        expression = "(" + str(curve["periodParam1"]) + ")" + " * math.pow(num_stories * (" + str(
            curve["periodParam0"]) + "), " + str(curve["periodParam2"]) + ")"
    else:
        expression = "0.0"

    return expression


def _save_comparison(name, doc, new_curve_set):
    original_curve_set = doc.copy()
    refactored_curve_set = new_curve_set.copy()
    print(name, "example:", doc["_id"], "saved")
    with open(name + "_original.json", "w") as f:
        original_curve_set["id"] = str(original_curve_set["_id"])
        del original_curve_set['_id']
        json.dump(original_curve_set, f, indent=2)
    with open(name + "_refactored.json", "w") as f:
        refactored_curve_set["id"] = str(refactored_curve_set["_id"])
        del refactored_curve_set["_id"]
        json.dump(refactored_curve_set, f, indent=2)


def _ls_renaming(legacy_ls_name_order):
    return "LS_" + str(legacy_ls_name_order)


def _add_demandtype_condition(demand_name):
    return demand_name + " > 0"


def convert_fragility_sets(fragility_collection, fragility_ids: list, save_exp=True, replace=False, insert_new=True):
    counts = {
        "StandardFragilityCurve": 0,
        "PeriodStandardFragilityCurve": 0,
        "ConditionalStandardFragilityCurve": 0,
        "CustomExpressionFragilityCurve": 0,
        "ParametricFragilityCurve": 0,
        "PeriodBuildingFragilityCurve": 0,
        "FragilityCurveRefactored": 0,
        "others": 0
    }

    refactored_fragility_ids = []
    for fragility_id in fragility_ids:
        try:
            new_curve_set = dict()
            doc = fragility_collection.find_one({"_id": ObjectId(fragility_id)})
            if doc["fragilityCurves"][0]["className"].endswith(".StandardFragilityCurve"):
                new_curve_set = convert_standard_fragility_set(doc)
                counts["StandardFragilityCurve"] += 1

            elif doc["fragilityCurves"][0]["className"].endswith(".PeriodStandardFragilityCurve"):
                new_curve_set = convert_period_standard_fragility_set(doc)
                counts["PeriodStandardFragilityCurve"] += 1

            elif doc["fragilityCurves"][0]["className"].endswith(".ConditionalStandardFragilityCurve"):
                new_curve_set = convert_conditional_standard_fragility_set(doc)
                counts["ConditionalStandardFragilityCurve"] += 1

            elif doc["fragilityCurves"][0]["className"].endswith(".CustomExpressionFragilityCurve"):
                new_curve_set = convert_custom_expression_fragility_curve(doc)
                counts["CustomExpressionFragilityCurve"] += 1

            elif doc["fragilityCurves"][0]["className"].endswith(".ParametricFragilityCurve"):
                new_curve_set = convert_parametric_fragility_curve(doc)
                counts["ParametricFragilityCurve"] += 1

            elif doc["fragilityCurves"][0]["className"].endswith(".PeriodBuildingFragilityCurve"):
                new_curve_set = convert_period_building_fragility_curve(doc)
                counts["PeriodBuildingFragilityCurve"] += 1

            elif doc["fragilityCurves"][0]["className"].endswith(".FragilityCurveRefactored"):
                counts["FragilityCurveRefactored"] += 1
                pass
            else:
                counts["others"] += 1
                print("cannot convert this fragility curve set: " + str(doc["_id"]))

            # uncomment to save and update database
            # save one example for comparison
            if save_exp:
                _save_comparison(fragility_id, doc, new_curve_set)
                refactored_fragility_ids.append(fragility_id)

            # update the database (replace)
            if replace and new_curve_set != {}:
                fragility_collection.replace_one({'_id': doc['_id']}, new_curve_set)
                print("update:", doc['_id'])
                refactored_fragility_ids.append(doc['_id'])

            # update the database (post new)
            if insert_new:
                del new_curve_set["_id"]
                refactored_fragility_id = fragility_collection.insert_one(new_curve_set).inserted_id
                print("insert:", refactored_fragility_id)
                refactored_fragility_ids.append(refactored_fragility_id)
        # catch failed cases so we can debug
        except:
            print("failed fragility curve:", fragility_id)
            print(traceback.format_exc())

    return counts, refactored_fragility_ids


if __name__ == "__main__":
    # dev/test/local
    uri = "mongodb://root:incorerocks@localhost:27019/?connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-256"
    # uri = "mongodb://root:incorerocks@localhost:27018/?connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-256"
    # uri = "mongodb://localhost:27017/?connectTimeoutMS=10000"
    client = MongoClient(uri)

    db = client['dfr3db']
    space_db = client['spacedb']
    fragility_collection = db['FragilitySet']

    # # only ids in "allowed spaces" can be refactored automatically
    # space_collection = space_db['Space']
    # allowed_spaces = ["ergo", "incore", "coe"]
    #
    # allowed_id_list = []
    # for space_doc in space_collection.find({"metadata.name" : { "$in" : allowed_spaces}}):
    #     for allowed_id in space_doc["members"]:
    #         if allowed_id not in allowed_id_list:
    #             allowed_id_list.append(allowed_id)

    # get all fragilties and cross compare with allowed ids
    fragility_ids = []
    for doc in fragility_collection.find():
        fragility_id = str(doc["_id"])
        # if fragility_id in allowed_id_list:
        #     fragility_ids.append(fragility_id)
        fragility_ids.append(fragility_id)

    # # local examples
    # fragility_ids = [
    #     "5b47c13d337d4a381cdf90a6",  # standard
    #     "5b47b2d8337d4a36187c7111",  # period standard with 0.2 sec sa
    #     "5b47b2d8337d4a36187c6c05",  # period building
    #     "5ed915895b6166000155d6ca",  # conditional
    #     "5b47ba6f337d4a3721059370",  # custom expression
    #     "5ed6bfc35b6166000155d0d9",  # parametric
    # ]

    stats, new_ids = convert_fragility_sets(fragility_collection, fragility_ids, save_exp=False, replace=True,
                                     insert_new=False)
    print(stats)

    # TODO: need to add new ids to a space if it's a new curve created (insert_new = True)
