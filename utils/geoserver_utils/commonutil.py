import xml.etree.ElementTree as ET
import json
import requests
import urllib.request
import pprint
import os

from sshtunnel import SSHTunnelForwarder
from bson import ObjectId
from pymongo import MongoClient

class CommonUtil:
    @staticmethod
    # save coveragestore.json in the same folder
    def get_coveragestore_json(geoserver_host):
        print("Obtaining coveragestore json")
        url = geoserver_host + "/rest/workspaces/incore/coveragestores.json"
        urllib.request.urlretrieve(url, "coveragestores.json")
        print("Done obtaining coveragestore json")

    @staticmethod
    def parse_name_from_coveragesotre_json():
        # https://incore-dev-kube.ncsa.illinois.edu/geoserver/rest/workspaces/incore/datastores.json
        # Opening JSON file
        f = open('coveragestores.json', )

        # returns JSON object as
        # a dictionary
        data = json.load(f)

        f.close()

        name_list = []
        coveragestores = data['coverageStores']['coverageStore']
        for coveragestore in coveragestores:
            name_list.append(coveragestore['name'])

        return name_list

    @staticmethod
    def get_mongo_server(mongo_host, mongo_user, mongo_keyfile, mongod_bind_host, mongo_bind_port):
        server = SSHTunnelForwarder(
            mongo_host,
            ssh_username=mongo_user,
            ssh_pkey=mongo_keyfile,
            remote_bind_address=(mongod_bind_host, mongo_bind_port)
        )

        return server

    @staticmethod
    def mongo_sshtunnel_test(mongo_host, mongo_user, mongo_keyfile, mongod_bind_host, mongo_bind_port, db_name):
        server = SSHTunnelForwarder(
            mongo_host,
            ssh_username=mongo_user,
            ssh_pkey=mongo_keyfile,
            remote_bind_address=(mongod_bind_host, mongo_bind_port)
        )

        server.start()

        client = MongoClient(mongod_bind_host, server.local_bind_port)  # server.local_bind_port is assigned local port
        db = client[db_name]
        pprint.pprint(db.collection_names())

        server.stop()

    @staticmethod
    def test_kube_mongo(mongo_bind_host, db_name):
        # kubectl port-forward incore-mongodb-0 27017:27017
        client = MongoClient(mongo_bind_host, 27020, username='username', password='password', authSource='admin')
        db = client[db_name]
        # db = client.get_database()
        print(db.name)
        print(client.server_info())
        # pprint,pprint(db.collection_names())
