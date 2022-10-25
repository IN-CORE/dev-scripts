import fiona
import uuid
import os
import geopandas as gpd
import sqlalchemy
import requests

from sqlalchemy import create_engine
from geojson import FeatureCollection
from config import Config as cfg


class NsiUtils():
    @staticmethod
    # this will download feature collection json by using county fips
    # fips: 15005
    def get_features_by_fips(state_county_fips):
        json_url = cfg.NSI_URL_FIPS + str(state_county_fips)
        result = requests.get(json_url)
        result.raise_for_status()
        result_json = result.json()

        collection = FeatureCollection(result_json['features'])

        gdf = gpd.GeoDataFrame.from_features(collection['features'])
        gdf = gdf.set_crs(epsg=4326)

        gdf = NsiUtils.add_columns_to_gdf(gdf, state_county_fips)

        return gdf

    @staticmethod
    # this will download zip file of geopackage by state using state fipes
    # Missouri: 29
    def download_nsi_data_state_file(state_fips):
        file_name = cfg.NSI_PREFIX + str(state_fips) + ".gpkg.zip"
        file_url = "%s/%s" % (cfg.NSI_URL_STATE, file_name)
        print("Downloading NSI data for the state: " + str(state_fips))
        r = requests.get(file_url, stream = True)

        download_filename = os.path.join("data", file_name)

        with open(download_filename,"wb") as zipfile:
            for chunk in r.iter_content(chunk_size=1024):
                # writing one chunk at a time to pdf file
                if chunk:
                    zipfile.write(chunk)

    @staticmethod
    # convert geopackage file to geodataframe
    def read_geopkg_to_gdf(infile):
        print("read GeoPackage")
        gpkgpd = None
        for layername in fiona.listlayers(infile):
            gpkgpd = gpd.read_file(infile, layer=layername, crs='EPSG:4326')

        return gpkgpd

    @staticmethod
    # add guid to geodataframe
    def add_guid_to_gdf(gdf):
        print("create guid column")
        for i, row in gdf.iterrows():
            guid_val = str(uuid.uuid4())
            gdf.at[i, 'guid'] = guid_val

        return gdf

    @staticmethod
    # add fips to geodataframe
    def add_columns_to_gdf(gdf, fips):
        print("create fips column")
        statefips = fips[:2]
        countyfips = fips[2:]
        for i, row in gdf.iterrows():
            guid_val = str(uuid.uuid4())
            gdf.at[i, 'guid'] = guid_val
            gdf.at[i, 'fips'] = fips
            gdf.at[i, 'statefips'] = statefips
            gdf.at[i, 'countyfips'] = countyfips

        return gdf

    @staticmethod
    # save new geopackage
    def df_to_geopkg(gdf, outfile):
        print("create output geopackage")
        gdf.to_file(outfile, driver="GPKG")

    @staticmethod
    # upload file to postgres
    def upload_postgres_from_gpk(infile):
        # read in the data
        gpkgpd = None
        for layername in fiona.listlayers(infile):
            gpkgpd = gpd.read_file(infile, layer=layername, crs='EPSG:4326')

        NsiUtils.upload_postgres_gdf(gpkgpd)

    @staticmethod
    # upload geodataframe to postgres
    def upload_postgres_gdf(gdf):
        try:
            # create the sqlalchemy connection engine
            db_connection_url = "postgresql://%s:%s@%s:%s/%s" % \
                                (cfg.DB_USERNAME, cfg.DB_PASSWORD, cfg.DB_URL, cfg.DB_PORT, cfg.DB_NAME)
            con = create_engine(db_connection_url)

            # Drop nulls in the geometry column
            print('Dropping ' + str(gdf.geometry.isna().sum()) + ' nulls.')
            gdf = gdf.dropna(subset=['geometry'])

            # Push the geodataframe to postgresql
            print('uploading GeoPackage to database')
            gdf.to_postgis("nsi_raw", con, index=False, if_exists='replace')

            con.dispose()

            print('uploading to database has finished.')

            return True

        except sqlalchemy.exc.OperationalError:
            print("Error in connecting database server")

            return False
