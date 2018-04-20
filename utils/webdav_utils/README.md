# README #

INCORE V2

## utilities for webdav ###

#### Import webdav data to INCORE V2 data repository ####

* To import the webdav data located in http://earthquake.ncsa.illinois.edu into incore data repository,
run 'python impor_webdav_data.py'

#### Parameters: ####
* rest_url: data repository rest endpoint URL (e.g: http://localhost:8080/data/api/datasets/)
* mongo_url = data repository mongodb url (e.g: localhost)
* data_repo_dir = local directory path for saving data (e.g: /home/data/)

## update dataType field in the database $$
* To update the dataType value based on mapping, set the variables in update_datatype_by_map.py 
* For example, mongo_url = "localhost", db_name = 'datadb', coll_name = 'Dataset', field_name = "dataType"