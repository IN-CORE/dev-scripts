# !/usr/bin/env python
"""
create_uuid_in_shapefile.py
Creates a new uuid field in the shapefile

Usage:
    create_uuid_in_shapefile.py IN_FILE OUT_FILE

Options:
    IN_FILE             Input shapefile name
    OUT_FILE            Output shapefile name
"""

import fiona
import uuid
import copy

from docopt import docopt

def main(arg):
    infilename = arg['IN_FILE']
    outfilename = arg['OUT_FILE']

    infile = fiona.open(infilename)

    # create list of each shapefile entry
    shape_property_list = []
    schema = infile.schema.copy()
    schema['properties']['guid'] = 'str:30'
    for in_feature in infile:
        # build shape feature
        tmp_feature = copy.deepcopy(in_feature)
        tmp_feature['properties']['guid'] = str(uuid.uuid4())
        shape_property_list.append(tmp_feature)

    with fiona.open(outfilename, 'w', 'ESRI Shapefile', schema) as output:
        print('create ouput line file........')
        for i in range(len(shape_property_list)):
            new_feature = shape_property_list[i]
            output.write(new_feature);

if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)