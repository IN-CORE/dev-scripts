import pandas as pd
import argparse
import os

# Create a csv file for each sheet in the excel file
# initialize argument parser
parser = argparse.ArgumentParser(description="Create csv files from excel file")
parser.add_argument("filename", help="Name of the excel file to be parsed")
parser.add_argument("output_dir", help="Name of the output directory")
args = parser.parse_args()

current_dir = os.getcwd()
op_dir = os.path.join(current_dir, args.output_dir)
if not os.path.exists(op_dir):
    os.mkdir(op_dir)


def create_csv(filename):
    base_caps = pd.read_excel(filename, sheet_name=[1, 2, 3, 4, 5])
    base_caps[1].to_csv(os.path.join(op_dir, "HH_base_val.csv"))
    base_caps[2].to_csv(os.path.join(op_dir, "GI_base_val.csv"))
    base_caps[3].to_csv(os.path.join(op_dir, "HH_base_val.csv"))
    base_caps[4].to_csv(os.path.join(op_dir, "FD_base_val.csv"))
    base_caps[5].to_csv(os.path.join(op_dir, "baseKAP.csv"))


if __name__ == "__main__":
    create_csv(args.filename)
    print("done")
