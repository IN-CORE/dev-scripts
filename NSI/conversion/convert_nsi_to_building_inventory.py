import pandas as pd
import os

from pyincore_data.nsiparser import NsiParser
from pyincore_data.nsibuildinginventory import NsiBuildingInventory
from pyincore_data.utils.nsiutil import NsiUtil


if __name__ == '__main__':
    in_file_path = "nsi_data/missing"
    out_file_path = "nsi_data"

    # reade state group csv file
    state_group = pd.read_csv("../StateToGroup_missing.csv")

    # create the combined state group dictionary
    STATE_REGION = dict(zip(state_group['Abbreviation'], state_group['Group']))

    # iterate with the STATE_REGION dictionary
    for state, region in STATE_REGION.items():
        # if it is geojson
        # in_file = os.path.join(json_path, f"{state}.geojson")
        # if it is geopackage
        in_file = os.path.join(in_file_path, f"{state}.gpkg")
        # check if json file exists
        if os.path.exists(in_file):
            out_gpkg = os.path.join(out_file_path, f"{state}.gpkg")
            print(f"State: {state}, Region: {region}")
            # create building inventory by geojson
            gdf = NsiBuildingInventory.convert_nsi_to_building_inventory_from_geojson(in_file, region)
            gdf.to_file(out_gpkg, driver='GPKG')
        else:
            print(f"State: {state}, Region: {region} - No GeoJSON file found")
