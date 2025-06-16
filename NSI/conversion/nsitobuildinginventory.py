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
