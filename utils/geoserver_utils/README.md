# README #

INCORE V2

## Utilities for geoserver ##

## set up working envirnment
use pip -r requirements.txt <br>
it could be easier to have anaconda to install all the necessary library<br>
[GDAL](https://pypi.python.org/pypi/GDAL)<br>
[gsconfig](https://pypi.python.org/pypi/gsconfig-py3)<br>
[rasterio](https://pypi.python.org/pypi/rasterio/1.0a12)<br>
[fiona](https://pypi.python.org/pypi/Fiona/1.7.11.post1)<br>
[shapely](https://pypi.python.org/pypi/Shapely/1.6.4.post1)<br>

## Clean up process
When there are some datasets exist in Geoserver but those dataset ids are not in the database, those dataset in the geoserver should be removed.<br>
There are script to do that by comparing the dataset ids in database and geoserver. If the dataset id in geoserver does not exist in the database, the dataset will be removed. <br>

Perform cleanup_incore_geoserver.py then perform fix_datastore_url.py

### cleanup_incore_geoserver.py
The first thing is to use cleanup_incore_geoserver.py
At the very top part of the code, there are some variables and these should be set correctly.
```
GEOSERVER_HOST: the url for the geoserver, such as "https://host_url/geoserver"
GEOSERVER_USER: geoserver user name
GEOSERVER_PW: geoserver password

MONGO_HOST: mongodb host url
MONGO_DB: database name that contains dataset info. Typically it is "datadb"
MONGO_USER: mongodb username
MONGO_PASS: mongodb password
MONGO_KEYFILE: mongodb server key file
MONGO_BIND_HOST: mongodb binding host url, usually "localhost" or "127.0.0.1"
MONGO_BIND_PORT: mongodb port, usually, 27017

BASE_DIR: the path that geoserver files are located, usually, "/opt/geoserver/data_dir/data/incore"
```
if you are not using the sshtunnel, you don't need to use mongo keyfile <br>

The other important setting is located at the top part of main()
```
    run_datastore = False
    run_wcs = False
    run_wfs = False
    run_wms = False
    remove_folders = True
```
Those are options for using what kind of information to use for removal. Suggest to make everything to True, except run_wms, since run_wms is problematic.<br>
Boolean remove_folders is little different that it removes the actual data files, whereas the others are removing the only entries in the configuration.

### fix_datastore_url.py
This file is to change the file path recorded in the configuration xml file. <br>
The configuration is located at the top of the code.
```
BASE_DIR: directory that files are located, usually "/opt/geoserver/data_dir/workspaces/incore/"
FIND_DIR_STR: the directory string that wants to find from the xml file, usually '/home/geoserver/data_dir/'
REPLACE_DIR_STR: the directory string that will be replaced as, usually '/opt/geoserver/data_dir/'
FIND_URL_STR: the url string that needs to be found, such as 'http://incore2-geoserver.ncsa.illinois.edu'
REPLACE_URL_STR: the url string that should be replaced as, such as 'https://incore-tst.ncsa.illinois.edu'
```
