"""
Script: nsibuildinginventory.py

Description:
    This script retrieves NSI (National Structure Inventory) data by county FIPS
    codes using the `NsiUtils` utility module. For each selected county, it:

    - Downloads NSI features as a GeoDataFrame,
    - Uploads the GeoDataFrame to a PostgreSQL/PostGIS database.

    Optional functionality (currently commented out) allows saving each GeoDataFrame
    to a GeoPackage (.gpkg) file locally.

Usage:
    python nsibuildinginventory.py

Assumptions:
    - The input FIPS file is located at: data\\us_county_fips_2018.csv
    - The script is currently limited to processing the first two FIPS entries
      from the file for testing/demo purposes.

Requirements:
    - pandas
    - Custom module: nsiutils.NsiUtils with methods:
        - get_features_by_fips(fips)
        - upload_postgres_gdf(gdf)
        - df_to_geopkg(gdf, path) (optional)

Output:
    - Uploads NSI data to a database (via NsiUtils)
    - Optionally writes .gpkg files to the `data/` directory
"""

import pandas as pd

from nsiutils import NsiUtils


def main():
    infile = ""
    in_fips_file = "data\\us_county_fips_2018.csv"

    # create fips list from fips file
    fips_list = create_county_fips_from_file(in_fips_file)

    for i in range(2):
        fips = fips_list[i]
        outfile = "data\\test" + str(fips) + ".gpkg"

        # get feature collection from NIS api
        gdf = NsiUtils.get_features_by_fips(fips)

        # upload geodataframe to database
        NsiUtils.upload_postgres_gdf(gdf)

        # # save gdf to geopackage
        # NsiUtils.df_to_geopkg(gdf, outfile)


def create_county_fips_from_file(infile):
    df = pd.read_csv(infile, dtype = {'GEOID': str})

    fips_list = df['GEOID'].tolist()

    return fips_list


if __name__ == '__main__':
    main()
