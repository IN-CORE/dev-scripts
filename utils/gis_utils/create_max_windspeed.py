import os
import fiona
import numpy as np
import json
import requests
from osgeo import gdal, osr


def main():
    # user define variables
    shp_folder = "C:\\Users\\ywkim\\Documents\\NIST\\Hurricane\\test\\"
    dataset_id = '5bdc5dec95c8b425a9300ace'
    shp_name = "hurricane_all.shp"
    rest_server = "http://incore2-services.ncsa.illinois.edu:8888/"
    out_file = "out_grid" # no extension needed
    ncols = 5  # the number of column will be the division of 100 of total x length
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

    # create placeholder
    grid = np.full([nrows, ncols], -9999)

    # create request header
    headers = {"X-Credential-Username": "ywkim"}

    for i in range(nrows):
        for j in range(ncols):
            x_coord = llx + (cell_size * i) + (cell_size / 2)
            y_coord = lly + (cell_size * j) + (cell_size / 2)
            hazard_url = rest_server + "hazard/api/hurricaneWindfields/%s/values?point=%f,%f&demandUnits=kmph&demandType=velocity" % (dataset_id, y_coord, x_coord)
            r = requests.get(url=hazard_url, headers = headers)
            hazard_json = r.json()[0]
            hazard_value = hazard_json["hazardValue"]
            print(y_coord, x_coord, hazard_value)
            if hazard_value != 'NaN':
                grid[nrows - 1 - i][j] = hazard_value

    create_ascii(out_asc, ncols, nrows, llx, lly, cell_size, grid)

    create_geotiff(out_asc, out_tif)

    os.remove(out_asc)


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
