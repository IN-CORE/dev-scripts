#!/usr/bin/env python3
"""
Script: convert_nsi_zip_to_inventory_gpkg.py

Description:
    This script automates the batch conversion of NSI ZIP archives containing
    GeoJSON files into building inventory GeoPackage (.gpkg) files, using
    pyincore_data's conversion utility. It also performs cleanup and
    zips the final .gpkg output for each state.

Functionality:
    - Loads a state-to-region group mapping from a CSV file (e.g., EastCoast, WestCoast, etc.).
    - Unzips each .zip file to extract its .geojson.
    - Converts the GeoJSON to a GPKG file using NSI-to-inventory logic.
    - Cleans up intermediate files, including GeoJSONs and temporary SQLite journal/index files.
    - Compresses the resulting GPKG file into a .zip archive stored in the `output_gpkg/` folder.

Usage:
    python convert_nsi_zip_to_inventory_gpkg.py [--input-dir INPUT_DIR]
                                                [--csv STATE_GROUP_CSV]
                                                [--output-dir OUTPUT_DIR]

Arguments:
    --input-dir     Directory containing NSI ZIP files (default: current directory)
    --csv           CSV file with columns: "Abbreviation", "Group" (default: state_groups.csv)
    --output-dir    Directory to store .gpkg and output ZIPs (default: current directory)

Requirements:
    - Python 3
    - pyincore-data
    - geopandas
    - A valid CSV file mapping state abbreviations to region groups

Outputs:
    - Zipped GPKG files stored in <output-dir>/output_gpkg/
    - All intermediate files are cleaned up automatically

Example:
    python convert_nsi_zip_to_inventory_gpkg.py --input-dir ./zips \
                                                --csv ./state_groups.csv \
                                                --output-dir ./gpkg_output
"""


import os
import zipfile
import csv
import argparse
from pyincore_data.nsibuildinginventory import NsiBuildingInventory


def load_state_group_map(csv_path):
    state_group_map = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            state_group_map[row["Abbreviation"].upper()] = row["Group"]
    return state_group_map


def cleanup_temp_files(state, input_dir, output_dir):
    geojson_path = os.path.join(input_dir, f"{state}.geojson")
    if os.path.exists(geojson_path):
        os.remove(geojson_path)
        print(f"[{state}] Removed temporary GeoJSON file.")

    tmp_suffixes = [
        "-journal",
        f".tmp_rtree_nsi_{state.lower()}.db"
    ]
    for suffix in tmp_suffixes:
        tmp_file = os.path.join(output_dir, f"{state}.gpkg{suffix}")
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
            print(f"[{state}] Removed temporary file: {tmp_file}")


def zip_gpkg_and_cleanup(state, gpkg_path, output_zip_dir):
    os.makedirs(output_zip_dir, exist_ok=True)
    zip_path = os.path.join(output_zip_dir, f"{state}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(gpkg_path, arcname=os.path.basename(gpkg_path))
    print(f"[{state}] GPKG zipped to: {zip_path}")

    os.remove(gpkg_path)
    print(f"[{state}] Removed original GPKG file after zipping.")


def convert_all_zips(input_dir, csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_zip_dir = os.path.join(output_dir, "output_gpkg")
    os.makedirs(output_zip_dir, exist_ok=True)

    state_group_map = load_state_group_map(csv_path)

    print("Starting batch conversion...")
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".zip"):
            continue

        state = os.path.splitext(filename)[0].upper()
        region_group = state_group_map.get(state)

        if not region_group:
            print(f"[{state}] Skipping: no region group found.")
            continue

        zip_path = os.path.join(input_dir, filename)
        geojson_name = f"{state}.geojson"
        geojson_path = os.path.join(input_dir, geojson_name)
        gpkg_path = os.path.join(output_dir, f"{state}.gpkg")

        print(f"[{state}] Unzipping {filename}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(input_dir)
            print(f"[{state}] Unzip complete.")
        except Exception as e:
            print(f"[{state}] Error during unzip: {e}")
            continue

        if not os.path.isfile(geojson_path):
            print(f"[{state}] GeoJSON file not found after unzip. Skipping.")
            continue

        print(f"[{state}] Starting conversion to {gpkg_path} using group '{region_group}'...")
        try:
            gdf = NsiBuildingInventory.convert_nsi_to_building_inventory_from_geojson(geojson_path, region_group)
            gdf.to_file(gpkg_path, driver="GPKG", layer=f"nsi_{state.lower()}")
            print(f"[{state}] Conversion complete. GPKG saved at {gpkg_path}")
        except Exception as e:
            print(f"[{state}] Error during conversion: {e}")
            continue
        finally:
            cleanup_temp_files(state, input_dir, output_dir)

        zip_gpkg_and_cleanup(state, gpkg_path, output_zip_dir)

    print("Batch conversion finished.")


def main():
    parser = argparse.ArgumentParser(description="Convert NSI ZIPs to building inventory GPKG files")
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Directory containing NSI ZIP files (default: current directory)"
    )
    parser.add_argument(
        "--csv",
        default="state_groups.csv",
        help="CSV file with state-group mapping (default: state_groups.csv)"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save .gpkg and output_gpkg ZIP files (default: current directory)"
    )
    args = parser.parse_args()

    convert_all_zips(args.input_dir, args.csv, args.output_dir)


if __name__ == "__main__":
    main()

