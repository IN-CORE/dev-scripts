# this is a script for counting the number of dataset in public space
# public space in here is incore and ergo space
# coe is not a public because it is only for the specific users

# this script should be run after port forwarding the mongodb from kube
# kubectl port-forwarding -n incore services/incore-mongodb 270**:27017


##################
# example report
##################
# •395 datasets (60% of them are hazard data) with 187 dataset types
# •1092 fragility curves
# •Earthquake
# •Tsunami
# •Flood
# •Tornado
# •Hurricane wind
# •Surge/wave
# •17 earthquake hazards
# •3 tornado hazards
# •12 tsunami hazards with diff intensities
# •2 hurricane wave/surge hazards

# coe: 5bcf2fcbf242fe047ce79db1
# ergo: 5a284f09c7d30d13bc0819a3
# incore: 5df8fd18b9219c068fb0257f


import pyincore
from pyincore import DataService, IncoreClient, FragilityService, HazardService, RepairService, RestorationService

def main():
    client = IncoreClient()
    datasvc = DataService(client)

    datasets_incore= datasvc.get_datasets(space="incore", limit=100000)
    datasets_ergo= datasvc.get_datasets(space="ergo", limit=100000)
    tot_dataset = get_union(datasets_ergo, datasets_incore)
    print(len(datasets_ergo), len(datasets_incore), tot_dataset)

    unique_datatype = []
    for dataset in datasets_incore:
        if dataset['dataType'] not in unique_datatype:
            unique_datatype.append(dataset['dataType'])
    tot_datatype = len(unique_datatype)
    print(tot_datatype)

    fragilitysvc = FragilityService(client)
    fragilities_incore = fragilitysvc.get_dfr3_sets(space="incore", limit=100000)
    fragilities_ergo = fragilitysvc.get_dfr3_sets(space="ergo", limit=100000)
    tot_fragility = get_union(fragilities_ergo, fragilities_incore)
    print(len(fragilities_ergo), len(fragilities_incore), tot_fragility)

    repairsvc = RepairService(client)
    repairs_ergo = repairsvc.get_dfr3_sets(space="ergo", limit=100000)
    repairs_incore = repairsvc.get_dfr3_sets(space="incore", limit=100000)
    tot_repair = get_union(repairs_ergo, repairs_incore)
    print(len(repairs_ergo), len(repairs_incore), tot_repair)

    restorationsvc = RestorationService(client)
    rest_ergo = restorationsvc.get_dfr3_sets(space="ergo", limit=100000)
    rest_incore = restorationsvc.get_dfr3_sets(space="incore", limit=100000)
    tot_restore = get_union(rest_ergo, rest_incore)
    print(len(rest_ergo), len(rest_incore), tot_restore)

    hazardsvc = HazardService(client)
    eq_ergo = hazardsvc.get_earthquake_hazard_metadata_list(space="ergo", limit=100000)
    eq_incore = hazardsvc.get_earthquake_hazard_metadata_list(space="incore", limit=100000)
    tot_eq = get_union(eq_ergo, eq_incore)
    print(len(eq_ergo), len(eq_incore), tot_eq)

    flood_ergo = hazardsvc.get_flood_metadata_list(space="ergo", limit=100000)
    flood_incore = hazardsvc.get_flood_metadata_list(space="incore", limit=100000)
    tot_flood = get_union(flood_ergo, flood_incore)
    print(len(flood_ergo), len(flood_incore), tot_flood)

    tornado_ergo = hazardsvc.get_tornado_hazard_metadata_list(space="ergo", limit=100000)
    tornado_incore = hazardsvc.get_tornado_hazard_metadata_list(space="incore", limit=100000)
    tot_tornado = get_union(tornado_ergo, tornado_incore)
    print(len(tornado_ergo), len(tornado_incore), tot_tornado)

    tsu_ergo = hazardsvc.get_tsunami_hazard_metadata_list(space="ergo", limit=100000)
    tsu_incore = hazardsvc.get_tsunami_hazard_metadata_list(space="incore", limit=100000)
    tot_tsunami = get_union(tsu_ergo, tsu_incore)
    print(len(tsu_ergo), len(tsu_incore), tot_tsunami)

    hurr_ergo = hazardsvc.get_hurricane_metadata_list(space="ergo", limit=100000)
    hurr_incore = hazardsvc.get_hurricane_metadata_list(space="incore", limit=100000)
    tot_hurr = get_union(hurr_ergo, hurr_incore)
    print(len(hurr_ergo), len(hurr_incore), tot_hurr)

    tot_hazard = tot_eq + tot_hurr + tot_tsunami + tot_flood + tot_tornado
    hazard_percentage = tot_hazard / tot_dataset * 100
    tot_curves = tot_fragility + tot_repair + tot_restore
    print("• " + str(tot_dataset) + " datasets (" + str(int(hazard_percentage)) + "% of them are hazard data) with " + str(tot_datatype) + " dataset types")
    print("• " + str(tot_curves) + " fragility, repair, and restoration curves")
    print("• Earthquake")
    print("• Tsunami")
    print("• Flood")
    print("• Tornado")
    print("• Hurricane wind")
    print("• Surge/wave")
    print("• " + str(tot_eq) + " earthquake hazards")
    print("• " + str(tot_tsunami) + " tsunami hazards with diff intensities")
    print("• " + str(tot_flood) + " flood hazards")
    print("• " + str(tot_tornado) + " tornado hazards")
    print("• " + str(tot_hurr) + " hurricane wave/surge hazards")

def get_union(list1, list2):
    union_items = []
    for item1 in list1:
        if item1["id"] not in union_items:
            union_items.append(item1["id"])
    for item2 in list2:
        if item2["id"] not in union_items:
            union_items.append(item2["id"])

    return len(union_items)

if __name__ == "__main__":
    main()