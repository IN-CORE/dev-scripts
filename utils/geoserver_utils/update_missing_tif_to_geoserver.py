import xml.etree.ElementTree as ET
import json
import requests
import urllib.request
import pprint
import os
import shutil
import tempfile
import zipfile36 as zipfile
import ntpath
import os
from os.path import splitext
from geoserver import util as gs_util
from geoserver.catalog import Catalog

from sshtunnel import SSHTunnelForwarder
from bson import ObjectId
from pymongo import MongoClient

from commonutil import CommonUtil as util

GEOSERVER_HOST = "https://incore/geoserver"
GEOSERVER_USER = ''
GEOSERVER_PW = ''
GEOSERVER_WORKSPACE = 'infore'

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = ""
MONGO_KEYFILE = "path_to_keyfile"

#CLUSTER = "local"
# CLUSTER = "dev"
CLUSTER = "prod"

TUNNEL_NEEDED = False

AUTH_TOKEN = ""

def main():
    mongo_host = None
    rest_url = None

    if CLUSTER == "local":
        mongo_host = "localhost"
        rest_url = "http://localhost:8080/data/api/datasets/"
    if CLUSTER == "dev":
        rest_url = "https://incore-dev.ncsa.illinois.edu/data/api/datasets/"
        mongo_host = '127.0.0.1'
        mongo_port = 27017
    if CLUSTER == "prod":
        rest_url = "https://incore.ncsa.illinois.edu/data/api/datasets/"
        mongo_host = '127.0.0.1'
        mongo_port = 27020

    coverage_list = create_geoserver_coverage_list()

    raster_dataset_list, dataset_name_list = query_raster_dataset_from_db(mongo_host, mongo_port)

    # check if the raster datasets have geoserver layer
    non_existing_data_list, non_exsisting_name_list = compare_db_geoserver(coverage_list, raster_dataset_list, dataset_name_list)

    zip_error_ids = []
    for dataset, filename in zip(non_existing_data_list, non_exsisting_name_list):
        # create temp directory
        tmp_data_dir = tempfile.mkdtemp()
        down_filename = os.path.join(tmp_data_dir, (filename + ".zip"))
        tif_name = os.path.join(tmp_data_dir, (filename + ".tif"))

        # download dataset to temp directory
        print("Downlodaing the data for " + str(dataset))
        auth_token = 'Bearer ' + str(AUTH_TOKEN)

        down_url = rest_url + dataset + "/blob"
        response = requests.get(down_url, headers={'Authorization': auth_token}, stream=True)
        if response.status_code == 200:
            with open(down_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # unzip downloaded file
            try:
                zip_ref = zipfile.ZipFile(down_filename, 'r')
                zip_ref.extractall(tmp_data_dir)
                zip_ref.close()

                update_raster_to_geoserver(dataset, tif_name)
            except zipfile.BadZipfile as err:
                zip_error_ids.append(dataset)
                print("OS error: {0}".format(err))


        # remove temp folder
        shutil.rmtree(tmp_data_dir)

def update_raster_to_geoserver(dataset, tif_name):
    # construct geoserver catalog
    gs_url = GEOSERVER_HOST + "/rest/"
    cat = Catalog(gs_url, GEOSERVER_USER, GEOSERVER_PW)
    # set workspace, if the workspace is not there, it has to be created
    worksp = cat.get_workspace(GEOSERVER_WORKSPACE)
    try:
        cat.create_coveragestore(dataset, tif_name, worksp)
        print("Raster " + dataset + " uploaded to utils")
    except:
        print(
            "There was an error uploading a raster " + dataset + ". Possibly the data already exist in the utils")
        pass

def compare_db_geoserver(coverage_list, raster_dataset_list, dataset_name_list):

    no_exist_id = []
    no_exist_name = []
    for dataset, dname in zip(raster_dataset_list, dataset_name_list):
        is_exist = False
        for coverage in coverage_list:
            if coverage == dataset:
                is_exist = True
                break
        if not is_exist:
            print("dataset " + dataset + " doesn't exist. Uploading to geoserver")
            no_exist_id.append(dataset)
            no_exist_name.append(dname)
        else:
            print("dataset " + dataset + " exist")

    print(len(no_exist_id))
    print(len(no_exist_name))
    print(no_exist_id)
    print(no_exist_name)

    return no_exist_id, no_exist_name


def create_geoserver_coverage_list():
    # Get coverage store json to see the list of coverages in the current geoserver
    print("obtaining coveragestore.json")
    util.get_coveragestore_json(GEOSERVER_HOST)
    name_list = util.parse_name_from_coveragesotre_json()

    return name_list

def query_raster_dataset_from_db(mongo_host, mongo_port):
    if TUNNEL_NEEDED:
        server = util.get_mongo_server(mongo_host)
        server.start()

        client = MongoClient(mongo_host, server.local_bind_port)  # server.local_bind_port is assigned local port
    else:
        # client = MongoClient(mongo_host, 27017)
        client = MongoClient(mongo_host, mongo_port, username=MONGO_USER, password=MONGO_PASS, authSource='admin')
        print(client.server_info())

    db = client[MONGO_DB]
    db.collection = db["Dataset"]

    result = db.Dataset.find({"$or": [{"format":"raster"},{"format":"geotif"}]})

    tif_ids = []
    filename_list = []

    for dictionary in result:
        doc = db.Dataset.find({'_id': dictionary["_id"]})
        for document in doc:
            doc_id = document["_id"]
            if ("fileDescriptors" in document):
                # check the number of fileDescriptors. if it is more than one that is not right
                file_descriptor = document["fileDescriptors"]
                filename = ""
                if len(file_descriptor) > 1:
                    print("The fileDescriptors in " + str(doc_id) + " has more than one file")
                else:
                    filename = file_descriptor[0]["filename"]
                    filenames = filename.split(".")
                    file_extension = filenames[-1]

                    if len(filenames) > 2:
                        del filenames[-1]
                        filename = '.'.join(filenames)
                    else:
                        filename = filenames[0]

                    if file_extension.lower() != "tif":
                        print("The file of " + str(doc_id) + " is not a tif but " + file_extension)
                    else :
                        tif_ids.append(str(doc_id))
                        filename_list.append(filename)
            else:
                print("The dataset " + str(doc_id) + " doesn't have fileDescriptors.")

    if TUNNEL_NEEDED:
        server.stop()

    return tif_ids, filename_list

if __name__ == '__main__':
    main()