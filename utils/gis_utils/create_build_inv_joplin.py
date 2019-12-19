import geopandas as gpd
import pandas as pd
import fiona
from shapely import geometry
from shapely.geometry import mapping, shape, Point

def main():
    shp_build_cen = "C:\\Users\\ywkim\\Documents\\NIST\\Joplin\\Nathanael\\joplin_bldg_cen.shp"
    shp_build_cen_tmp = "C:\\Users\\ywkim\\Documents\\NIST\\Joplin\\Nathanael\\joplin_bldg_cen_tmp.shp"
    csv_addr_pt = "C:\\Users\\ywkim\\Documents\\NIST\\Joplin\\Nathanael\\IN-CORE_2ev2_SetupJoplin_FourInventories_2019-08-01_addresspointinventory.csv"

    # create strictid in the input shapefile
    is_create = create_strctid_in_shp(shp_build_cen, shp_build_cen_tmp)

    if is_create != True:
        print("strctid filed is already in there")
        return

    # read point shapefile using geopandas
    gdf_build_cen = gpd.read_file(shp_build_cen_tmp)
    df_addr_pt = pd.read_csv(csv_addr_pt)
    df_addr_pt = df_addr_pt.apply(pd.to_numeric, errors='ignore', downcast='integer')

    join = gdf_build_cen.merge(df_addr_pt, on='strctid', how='left')
    # geometry = [Point(xy) for xy in zip(join.geometry_x.astype(float), join.geometry_y.astype(float))]
    # after join, there are two geometry filed because both gdf_build_cen and df_addr_pt has a geometry field
    # the name became geometry_x(gdf_build_cen) and geometry_y (df_addr_pt)
    # in here, we need the geometry from gdf_build_cen so will use geometry_x as the geometyr
    crs = {'init': 'epsg:4326'}
    join['geometry'] = join.apply(lambda row: Point(row.geometry_x.x, row.geometry_x.y), axis=1)
    join = join.drop(['geometry_x', 'geometry_y', 'ap4326', 'x', 'y'], axis=1)
    join = join.apply(pd.to_numeric, errors='ignore')
    gdf = gpd.GeoDataFrame(join, crs=crs, geometry=join.geometry)
    gdf.to_file("C:\\Users\\ywkim\\Documents\\NIST\\Joplin\\Nathanael\\result2.shp")


def create_strctid_in_shp(shp_build_cen, shp_build_cen_tmp):
    with fiona.open(shp_build_cen, 'r') as input:
        schema = input.schema.copy()
        input_crs = input.crs
        try:
            print(schema['properties']['objectid'])
        except:
            print("objectid field does not exist")
            return False

        try:
            print(schema['properties']['strctid'])
            return False
        except:
            schema['properties']['strctid'] = 'str:10'
            with fiona.open(shp_build_cen_tmp, 'w', 'ESRI Shapefile', schema, input_crs) as output:
                for elem in input:
                    objectid = elem['properties']['objectid']
                    strctid = "S00" + str(objectid).zfill(5)
                    elem['properties']['strctid'] = strctid
                    output.write({'properties': elem['properties'], 'geometry': mapping(shape(elem['geometry']))})
            return True

if __name__ == "__main__":
    main()