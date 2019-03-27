import os
import fiona
import numpy as np
import geopandas as gpd
import requests
from osgeo import gdal, osr
from shapely.geometry import Polygon, Point


def main():
    # user define variables
    shp_folder = "C:\\Users\\ywkim\\Documents\\NIST\\Hurricane\\test\\"
    shp_name = "hurricane_all.shp"
    spd_field_api = "hazardValue"
    spd_field = "velocity"
    # shp_name = "5a284f0bc7d30d13bc081a28.shp"
    rest_server = "http://incore2-services.ncsa.illinois.edu:8888/"
    out_file = "out_grid" # no extension needed
    headers = {"X-Credential-Username": "ywkim"} # request header
    ncols = 50  # the number of column will be the division of 100 of total x length
    # the number of rows will be decided based on the cell size calculated from above

    # other variables
    shp_location = shp_folder + shp_name
    shape = fiona.open(shp_location)
    bbox = get_bbox_from_shp(shape)
    out_asc = out_file + ".asc"
    out_tif = out_file + ".tif"

    llx = bbox[0]
    lly = bbox[1]

    length_x = bbox[2] - bbox[0]
    length_y = bbox[3] - bbox[1]

    cell_size = length_x / ncols
    nrows = int(length_y / cell_size + 1)
    tot_cell = ncols * nrows

    # create placeholder
    grid = np.full([nrows, ncols], -9999)

    # read point shapefile using geopandas
    points = gpd.read_file(shp_location)

    k = 0
    for i in range(nrows):
        for j in range(ncols):
            msg = str(tot_cell - k) + " iteration left"
            print(msg)
            x_coord = llx + (cell_size * j) + (cell_size / 2)
            y_coord = lly + (cell_size * i) + (cell_size / 2)

            # get hazard value using rest api
            # hazard_value = get_hazard_value_from_api(dataset_id, x_coord, y_coord, rest_server, headers, spd_field_api)
            #if hazard_value != 'NaN':
            #    grid[nrows - 1 - i][j] = hazard_value

            # get hazard value using shape overlay
            hazard_value = get_hazard_value_from_bbox(x_coord, y_coord, cell_size, points, spd_field)

            if hazard_value > 0:
                grid[nrows - 1 - i][j] = hazard_value

            k+= 1

    create_ascii(out_asc, ncols, nrows, llx, lly, cell_size, grid)

    create_geotiff(out_asc, out_tif)

    os.remove(out_asc)

def get_hazard_value_from_bbox(x_coord, y_coord, cell_size, points, spd_field):
    hazard_value = 0
    lon_coord_list = [x_coord - (cell_size / 2), x_coord + (cell_size / 2), x_coord + (cell_size / 2), x_coord - (cell_size / 2), x_coord - (cell_size / 2)]
    lat_coord_list = [y_coord - (cell_size / 2), y_coord - (cell_size / 2), y_coord + (cell_size / 2), y_coord + (cell_size / 2), y_coord - (cell_size / 2)]
    poly_geom = Polygon(zip(lon_coord_list, lat_coord_list))

    selection = points[points.within(poly_geom)]

    if len(selection) > 0:
        hazard_value = selection[spd_field].max()
        # use this to save the selection and bbox as shapefile
        # selection.to_file(filename='selection.shp', driver="ESRI Shapefile")
        # # bbox_poly.to_file(filename='bbox_poly.geojson', driver='GeoJSON')
        # crs = {'init': 'epsg:4326'}
        # bbox_poly = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[poly_geom])
        # bbox_poly.to_file(filename='bbox_poly.shp', driver="ESRI Shapefile")

    return hazard_value


def get_hazard_value_from_api(dataset_id, x_coord, y_coord, rest_server, headers, spd_field):
    hazard_url = rest_server + "hazard/api/hurricaneWindfields/%s/values?point=%f,%f&demandUnits=kmph&demandType=velocity" % (
    dataset_id, y_coord, x_coord)
    r = requests.get(url=hazard_url, headers=headers)
    hazard_json = r.json()[0]
    hazard_value = hazard_json[spd_field]

    return hazard_value

def create_geotiff(in_asc, out_tif):
    drv = gdal.GetDriverByName('GTiff')
    ds_in = gdal.Open(in_asc)
    ds_out = drv.CreateCopy('out.tif', ds_in)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    ds_out.SetProjection(srs.ExportToWkt())
    ds_in = None
    ds_out = None


def create_ascii(outfile, ncols, nrows, xll, yll, cell_size, grid):
    header = "ncols %d \nnrows %d\nxllcorner %f\nyllcorner %f\ncellsize %f\nnodata_value -9999" % (
    int(ncols), int(nrows), xll, yll, cell_size)
    np.savetxt(outfile, grid, fmt='%f', header=header, comments='', delimiter=' ', newline='\n')


def get_bbox_from_shp(shape):
    try:
        bbox_col = shape.bounds
        bbox = [bbox_col[0], bbox_col[1], bbox_col[2], bbox_col[3]]
        shape.close()
        return bbox
    except IOError as err:
        print("IO error: {0}".format(err))


if __name__ == "__main__":
    main()
