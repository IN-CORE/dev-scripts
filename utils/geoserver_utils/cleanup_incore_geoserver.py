import xml.etree.ElementTree as ET
import json
import requests
import urllib.request
import pprint

from sshtunnel import SSHTunnelForwarder
from bson import ObjectId
from pymongo import MongoClient

GEOSERVER_HOST = "https://host_url/geoserver"
GEOSERVER_USER = 'admin'
GEOSERVER_PW = ''

MONGO_HOST = "mongo.ncsa.illinois.edu"
MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

def main():
    run_datastore = False
    run_wcs = False
    run_wfs = False
    run_wms = False

    # delete using datastore
    if run_datastore:
        get_datastore_json()
        name_list = parse_name_from_datasotre_json()

        # check if it is in the dsatabase and remove datastore
        remove_list = create_remove_store_list_using_wcs(name_list, False)
        # name_list = parse_name_from_datasotre_json()
        print("There are " + str(len(remove_list)) + " datasets to be removed")

        remove_stores(remove_list, 'wfs')

    # delete using wcs
    if run_wcs:
        get_service_xml("wcs")
        wcs_name_list, wcs_keyword_list = parse_name_from_wcs_getcapabilities()

        # check if it is in the database and remove datastore
        remove_list = create_remove_store_list_using_wcs(wcs_name_list)
        print("There are" + str(len(remove_list)) + " datasets to be removed")

        remove_stores(remove_list, 'wcs')

    if run_wfs:
        get_service_xml("wfs")
        wfs_name_list, wfs_title_list = parse_name_from_wfs_getcapabilities()

        # check if it is in the dsatabase and remove datastore
        remove_list = create_remove_store_list_using_wcs(wfs_name_list)
        # name_list = parse_name_from_datasotre_json()
        print("There are " + str(len(remove_list)) + " datasets to be removed")

        remove_stores(remove_list, 'wfs')

    # TODO this doesn't work because the wms file getting broken when there is broken SRS
    if run_wms:
        get_service_xml("wms")
        name_list, title_list = parse_name_from_wms_getcapabilities()
        print("There are" + str(len(remove_list)) + " datasets to be removed")

    # name_list, title_list = parse_name_from_wfs_getcapabilities()
    # print(len(name_list))

def remove_stores(ids, flag):
    total = len(ids)

    if flag == "wcs":
        base_url = GEOSERVER_HOST + "/rest/workspaces/incore/coveragestores/"

    if flag == "wfs":
        base_url = GEOSERVER_HOST + "/rest/workspaces/incore/datastores/"

    for index, id in enumerate(ids):
        url = base_url + id +"?recurse=true"
        response = requests.delete(url, auth=(GEOSERVER_USER, GEOSERVER_PW))
        if response.status_code != 200:
            #print("Removed id of " + id)
            print("Failed to remove id of " + id)
        left = total-index
        if left % 100 == 0:
            print(str(left) + " iterations left")
    print("finished remove")

def create_remove_store_list_using_wcs(name_list, is_parse=True):
    remove_list = []
    server = get_mongo_server()
    server.start()

    client = MongoClient(MONGO_BIND_HOST, server.local_bind_port)  # server.local_bind_port is assigned local port
    db = client[MONGO_DB]
    db.collection = db["Dataset"]
    collection = db.collection

    i = 0
    for name in name_list:
        # split workspace and storename
        if is_parse:
            names = name.split(':')
            store_name = names[1]
        else:
            store_name = name

        # check if dataset exists
        try:
            is_dataset, id = check_if_dataset_exists(store_name, collection)
        except Exception as e:
            print("Failed to check " + str(store_name) + " in the database")
            print(e)
            is_dataset = True
        if is_dataset is False:
            remove_list.append(id)
        i += 1
        # if i > 1000:
        #     break

    server.stop()

    return remove_list

def parse_name_from_datasotre_json():
    # https://incore-dev-kube.ncsa.illinois.edu/geoserver/rest/workspaces/incore/datastores.json
    # Opening JSON file
    f = open('datastores.json', )

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    f.close()

    name_list = []
    datastores = data['dataStores']['dataStore']
    for datastore in datastores:
        name_list.append(datastore['name'])

    return name_list

def parse_name_from_wms_getcapabilities():
    # https://incore-dev-kube.ncsa.illinois.edu/geoserver/incore/ows?service=WMS&version=1.0.0&request=GetCapabilities
    name_list = []
    title_list = []

    tree = ET.parse('wms-getcapabilities.xml')
    root = tree.getroot()
    layer_list = (((root.find("Capability")).find("Layer")).findall("Layer"))

    for layer in layer_list:
        name = layer_list[0].find('Name').text
        title = layer_list[0].find('Title').text
        name_list.append(name)
        title_list.append(title)

    return name_list, title_list

def parse_name_from_wcs_getcapabilities():
    # https://incore-dev-kube.ncsa.illinois.edu/geoserver/incore/ows?service=WCS&version=1.0.0&request=GetCapabilities
    name_list = []
    keyword_list = []

    tree = ET.parse('wcs-getcapabilities.xml')
    root = tree.getroot()
    coveragelist = (root.find("{http://www.opengis.net/wcs}ContentMetadata")).findall("*")
    for coverage in coveragelist:
        name = coverage.find("{http://www.opengis.net/wcs}name").text
        keyword = coverage.find("{http://www.opengis.net/wcs}keywords").findall("*")[0].text
        name_list.append(name)
        keyword_list.append(keyword)

    return name_list, keyword_list

def parse_name_from_wfs_getcapabilities():
    # https://incore-dev-kube.ncsa.illinois.edu/geoserver/incore/ows?service=WFS&version=1.0.0&request=GetCapabilities
    name_list = []
    title_list = []

    tree = ET.parse('wfs-getcapabilities.xml')
    root = tree.getroot()
    featuretypelist = root.find("{http://www.opengis.net/wfs}FeatureTypeList")
    featuretypes = featuretypelist.findall(("{http://www.opengis.net/wfs}FeatureType"))

    for featuretype in featuretypes:
        name = featuretype.find("{http://www.opengis.net/wfs}Name").text
        title = featuretype.find("{http://www.opengis.net/wfs}Title").text
        name_list.append(name)
        title_list.append(title)

    return name_list, title_list

def check_if_dataset_exists(store_name, collection):
    ids = store_name.split('.')
    id = ids[0]
    objectid = ObjectId(id)
    db_data =  collection.find({'_id': objectid})
    data_list = list(db_data)
    if len(data_list) > 0:
        return True, id
    else:
        return False, id

def get_mongo_server():
    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_pkey=MONGO_KEYFILE,
        remote_bind_address=(MONGO_BIND_HOST, MONGO_BIND_PORT)
    )

    return server

def mongo_sshtunnel_test():
    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_pkey=MONGO_KEYFILE,
        remote_bind_address=(MONGO_BIND_HOST, MONGO_BIND_PORT)
    )

    server.start()

    client = MongoClient(MONGO_BIND_HOST, server.local_bind_port)  # server.local_bind_port is assigned local port
    db = client[MONGO_DB]
    pprint.pprint(db.collection_names())

    server.stop()

def test_kube_mongo():
    # kubectl port-forward incore-mongodb-0 27017:27017
    client = MongoClient(MONGO_BIND_HOST, 27017, username='username', password='password', authSource='admin')
    db = client[MONGO_DB]
    db = client[MONGO_DB]
    # db = client.get_database()
    print(db.name)
    print(client.server_info())
    # pprint,pprint(db.collection_names())

def get_service_xml(flag):
    try:
        if flag == "wcs":
            print("Obtaining WCS file")
            url = GEOSERVER_HOST + "/incore/ows?service=WCS&version=1.0.0&request=GetCapabilities"
            urllib.request.urlretrieve(url, "wcs-getcapabilities.xml")
            print("Done obtaining WCS file")

        if flag == "wfs":
            print("Obtaining WFS file")
            url = GEOSERVER_HOST + "/incore/ows?service=WFS&version=1.0.0&request=GetCapabilities"
            # print(url)
            urllib.request.urlretrieve(url, "wfs-getcapabilities.xml")
            print("Done obtaining WFS file")

        if flag == "wms":
            print("Obtaining WMS file")
            url = GEOSERVER_HOST + "/incore/ows?service=WMS&version=1.0.0&request=GetCapabilities"
            urllib.request.urlretrieve(url, "wms-getcapabilities.xml")
            print("Done obtaining WMS file")
    except Exception:
        raise("There was an error obtaining list from geoserver")

def get_datastore_json():
    print("Obtaining datastore json")
    url = GEOSERVER_HOST + "/rest/workspaces/incore/datastores.json"
    urllib.request.urlretrieve(url, "datastores.json")
    print("Done obtaining datastore json")

if __name__ == '__main__':
    main()

