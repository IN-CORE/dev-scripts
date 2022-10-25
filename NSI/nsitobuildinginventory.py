import fiona
import uuid
import os
import geopandas as gpd
import sqlalchemy
import requests

from sqlalchemy import create_engine
from config import Config as cfg

# download NSI dataset

# read NSI geopackage
# TODO this is a method of using geopandas.
#  However, even though this method has more advantage,
#  the saving to geopackage output has a crs error due to the fiona problem

def main(infile, outfile):
    # read geopackage
    gpkgpd = read_geopkg_to_gdf(infile)

    # add guid
    gpkgpd = add_guid_to_geopkg(gpkgpd)

    # upload geopackage to database
    upload_postgres_gdf(gpkgpd)

def download_nsi_data(state_fips):
    file_name = cfg.NSI_PREFIX + str(state_fips) + ".gpkg.zip"
    file_url = "%s/%s" % (cfg.NSI_URL, file_name)
    print("Dowloading NSI data for the state: " + str(state_fips))
    r = requests.get(file_url, stream = True)
    # r = requests.get(file_url)
    download_filename = os.path.join("data", file_name)

    with open(download_filename,"wb") as zipfile:
        for chunk in r.iter_content(chunk_size=1024):
            # writing one chunk at a time to pdf file
            if chunk:
                zipfile.write(chunk)
        # zipfile.write(r.content)

def read_geopkg_to_gdf(infile):
    print("read GeoPackage")
    gpkgpd = None
    for layername in fiona.listlayers(infile):
        gpkgpd = gpd.read_file(infile, layer=layername, crs='EPSG:4326')

    return gpkgpd

# add guid to geodataframe
def add_guid_to_geopkg(gpkgpd):
    print("create guid column")
    for i, row in gpkgpd.iterrows():
        guid_val = str(uuid.uuid4())
        gpkgpd.at[i, 'guid'] = guid_val

    return gpkgpd

# save new geopackage
def df_to_geopkg(in_gdf):
    print("create output geopackage")
    in_gdf.to_file(outfile, driver="GPKG")

# upload file to postgres
def upload_postgres_from_gpk(infile):
    # read in the data
    gpkgpd = None
    for layername in fiona.listlayers(infile):
        gpkgpd = gpd.read_file(infile, layer=layername, crs='EPSG:4326')

    upload_postgres_gdf(gpkgpd)

# upload geodataframe to postgres
def upload_postgres_gdf(in_gdf):
    try:
        # create the sqlalchemy connection engine
        db_connection_url = "postgresql://%s:%s@%s:%s/%s" % \
                            (cfg.DB_USERNAME, cfg.DB_PASSWORD, cfg.DB_URL, cfg.DB_PORT, cfg.DB_NAME)
        con = create_engine(db_connection_url)

        # Drop nulls in the geometry column
        print('Dropping ' + str(in_gdf.geometry.isna().sum()) + ' nulls.')
        in_gdf = in_gdf.dropna(subset=['geometry'])

        # Push the geodataframe to postgresql
        print('uploading GeoPackage to database')
        in_gdf.to_postgis("nsi_raw", con, index=False, if_exists='replace')

        con.dispose()

        print('uploading to database has finished.')

        return True

    except sqlalchemy.exc.OperationalError:
        print("Error in connecting database server")

        return False


# def read_nsi_data(infile, outfile):
#     infile = fiona.open(infile)
#
#     # add GUID field
#     infile = add_guid(infile, outfile)
#     print(infile)
#
# # add GUID field
# def add_guid(infile, outfile):
#     # create list of each shapefile entry
#     shape_property_list = []
#     schema = infile.schema.copy()
#     schema['properties']['guid'] = 'str:30'
#     for in_feature in infile:
#         # build shape feature
#         tmp_feature = copy.deepcopy(in_feature)
#         tmp_feature['properties']['guid'] = str(uuid.uuid4())
#         shape_property_list.append(tmp_feature)
#
#     with fiona.open(outfile, 'w', 'GPKG', schema) as output:
#         print('create output geopackage........')
#         for i in range(len(shape_property_list)):
#             new_feature = shape_property_list[i]
#             output.write(new_feature)

# convert the values

# renamd the fields

# add missing fields

# save as geopackage

if __name__ == '__main__':
    # from osgeo import osr
    # sp = osr.SpatialReference()
    # target_crs = 'PROJCS["Geographic",GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]]'
    # sp.ImportFromWkt(target_crs)
    # sp.ExportToWkt()
    infile = "C:\\Users\\ywkim\\Documents\\NIST\\NSI\\joplin.gpkg"
    outfile = "C:\\Users\\ywkim\\Documents\\NIST\\NSI\\test.gpkg"
    # read_nsi_data(infile, outfile)
    # upload_postgres(infile)
    # download_nsi_data(44)
    gdf = read_geopkg_to_gdf(infile)
    upload_postgres_gdf(gdf)