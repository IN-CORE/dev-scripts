"""
Script: convert_nsi_to_building_inventory.py

Description:
    This script converts a set of NSI GeoPackage (.gpkg) files into IN-CORE-compatible
    building inventory GeoPackages using the pyincore_data library.

    It reads a CSV file mapping state abbreviations to regional groups, iterates
    over each state, and applies the appropriate regional conversion logic.

    The resulting converted building inventories are saved as GeoPackage (.gpkg)
    files in the output directory.

Usage:
    python convert_nsi_to_building_inventory.py

Assumptions:
    - Input files are stored in the directory: nsi_data/missing/
    - Output files are saved to the directory: nsi_data/
    - The input GeoPackage file for each state is named <STATE>.gpkg
    - The CSV file `../StateToGroup_missing.csv` maps state abbreviations to region groups

Requirements:
    - Python packages: pandas, pyincore_data
    - Input GeoPackage files must exist for states listed in the CSV

Output:
    - One GeoPackage file per state saved to `nsi_data/`, named <STATE>.gpkg
    - Skips states for which input files do not exist
"""


import pandas as pd
import os

from pyincore_data.nsiparser import NsiParser
from pyincore_data.nsibuildinginventory import NsiBuildingInventory
from pyincore_data.utils.nsiutil import NsiUtil


if __name__ == '__main__':
    in_file_path = "nsi_data/missing"
    out_file_path = "nsi_data"

    # reade state group csv file
    state_group = pd.read_csv("StateToGroup_missing.csv")

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
