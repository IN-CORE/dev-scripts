# This script will catch and remove orphan dataset (dataset with no space).
# First, it gives space to all the orphan datasets.
# The reason for doing this is for clean deletion of the dataset
# The dataset only can be removed by using the deletion rest end point
# Otherwise, such as, just deleting from database will remain data files in data repo and geoserver
# However, deletion endpoint will not be able to delete any dataset without space
# Therefore, it will give the space info to orphan datasets first, then remove those.

import requests

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

#CLUSTER = "local"
# CLUSTER = "dev"
CLUSTER = "prod"

UPDATE_DB = True
REMOVE_DATASET = True
TUNNEL_NEEDED = False

AUTH_TOKEN = ""

def main():
    mongo_host = None
    rest_url = None

    if CLUSTER == "local":
        mongo_host = "localhost"
        orphan_space_id = "5d0811315648c40487fecf42"
        rest_url = "http://localhost:8080/data/api/datasets/"
    if CLUSTER == "tst":
        orphan_space_id = "5d0811315648c40487fecf42"
        rest_url = "https://incore-dev-kube.ncsa.illinois.edu/data/api/datasets/"
        mongo_host = "127.0.0.1"  # when using kube forwarder
        mongo_port = 27017
        mongo_user = ''
        mongo_password = ''
    if CLUSTER == "dev":
        orphan_space_id = "5d0811315648c40487fecf42"
        rest_url = "https://incore-dev.ncsa.illinois.edu/data/api/datasets/"
        mongo_host = "127.0.0.1"    # when using kube forwarder
        mongo_port = 27017
        mongo_user = ''
        mongo_password = ''
    if CLUSTER == "prod":
        # mongo_host = "incore2-mongo1.ncsa.illinois.edu"
        mongo_host = "127.0.0.1"    # when using kube forwarder
        orphan_space_id ="5d081106b9219c065b4cdfc0"
        rest_url = "https://incore.ncsa.illinois.edu/data/api/datasets/"
        mongo_port = 27017
        mongo_user = ''
        mongo_password = ''

    if TUNNEL_NEEDED:
        server = get_mongo_server(mongo_host)
        server.start()

        client = MongoClient(MONGO_BIND_HOST, server.local_bind_port)  # server.local_bind_port is assigned local port
    else:
        # client = MongoClient(mongo_host, mongo_port)
        client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_password, authSource='admin')
        print(client.server_info())

    datadb = client['datadb']
    spacedb = client['spacedb']
    dataset_collection = datadb['Dataset']
    space_collection = spacedb['Space']

    orphan_dataset_list = []

    for dataset in dataset_collection.find():
        dataset_id = str(dataset["_id"])
        orphan = True
        for space in space_collection.find():
            if "members" in space and dataset_id in list(space["members"]):
                orphan = False
                break

        if orphan:
            print(str(dataset_id) + " is orphan")
            orphan_dataset_list.append(dataset_id)

            # move that dataset to the orphan space
            orphan_space = space_collection.find_one({"_id": ObjectId(orphan_space_id)})
            orphan_space["members"].append(dataset_id)

            if UPDATE_DB:
                space_collection.replace_one({'_id': orphan_space['_id']}, orphan_space)
                print("move dataset id: " + dataset_id + " to orphan space")

    print(orphan_dataset_list)

    # delete orphans
    if REMOVE_DATASET:
        print("Starting remove process")
        error_ids = []
        for doc_id in orphan_dataset_list:
            delete_url = rest_url + str(doc_id)
            auth_token = 'Bearer ' + str(AUTH_TOKEN)
            response = requests.delete(delete_url, headers={'Authorization': auth_token})
            if response.status_code == 200:
                print(str(doc_id) + " deleted.")
            else:
                print("Failed to delete " + str(doc_id))
                error_ids.append(doc_id)
                pass

        print(error_ids)

    if TUNNEL_NEEDED:
        server.stop()

def get_mongo_server(mongo_host):
    server = SSHTunnelForwarder(
        mongo_host,
        ssh_username=MONGO_USER,
        ssh_pkey=MONGO_KEYFILE,
        remote_bind_address=(MONGO_BIND_HOST, MONGO_BIND_PORT)
    )

    return server

if __name__ == "__main__":
    main()