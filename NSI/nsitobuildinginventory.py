import fiona
import uuid
import copy
import geopandas as gpd

# download NSI dataset

# read NSI geopackage
# TODO this is a method of using geopandas.
#  However, even though this method has more advantage,
#  the saving to geopackage output has a crs error due to the fiona problem

def read_nsi_data(infile, outfile):
    gpkgname = ""
    gpkgpd = None
    for layername in fiona.listlayers(infile):
        gpkgpd = gpd.read_file(infile, layer=layername, crs='EPSG:4326')
        gpkgname = layername
    gpkgpd.to_file(outfile, layer=layername, driver="GPKG")

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
#     schema['properties']['uuid'] = 'str:30'
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
    read_nsi_data(infile, outfile)