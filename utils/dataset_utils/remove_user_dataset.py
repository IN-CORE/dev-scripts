"""
This script will scan and remove all the dataset created by certain user
First, it will remove the hazard datasets, then will remove regular datasets.
Set MONGO_USER and MONGO_KEYFILE
If you want to use tunnel to connect mongodb make TUNNEL_NEEDED to True
"""
import requests

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient

MONGO_DATA_DB = "datadb"
MONGOD_HAZARD_DB = "hazarddb"
MONGO_USER = ""
MONGO_PASS = ""
MONGO_KEYFILE = "path_to_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = "27017"

#CLUSTER = "local"
#CLUSTER = "dev"
#CLUSTER = "tst"
CLUSTER = "prod"

REMOVE_DATASET = True
TUNNEL_NEEDED = False

AUTH_TOKEN = ""

USER_NAME = ""

def main():
	mongo_host = None
	rest_url = None

	if CLUSTER == "local":
		mongo_host = "localhost"
		rest_url = "http://localhost:8080/"
	if CLUSTER == "dev":
		rest_url = "https://incore-dev.ncsa.illinois.edu/"
		mongo_host = "127.0.0.1"
		mongo_port = 27017
	if CLUSTER == "tst":
		rest_url = "https://incore-tst.ncsa.illinois.edu/"
		mongo_host = "127.0.0.1"
		mongo_port = 27018
	if CLUSTER == "prod":
		rest_url = "https://incore.ncsa.illinois.edu/"
		mongo_host = "127.0.0.1"
		mongo_port = 27020

	if TUNNEL_NEEDED:
		server = get_mongo_server(mongo_host)
		server.start()

		client = MongoClient(mongo_host, server.local_bind_port)  # server.local_bind_port is assigned local port
	else:
		# client = MongoClient(MONGO_BIND_HOST, 27017)
		client = MongoClient(mongo_host, mongo_port, username=MONGO_USER, password=MONGO_PASS, authSource='admin')
		print(client.server_info())

	eq_dataset_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "EarthquakeDataset")
	eq_model_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "EarthquakeModel")
	flood_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "FloodDatset")
	hurricane_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "HurricaneDataset")
	hurricane_wf_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "HurricaneWindfields")
	scenario_eq_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "ScenarioEarthquake")
	scenario_tornado_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "ScenarioTornado")
	tornado_dataset_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "TornadoDataset")
	tornado_model_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "TornadoModel")
	tsunami_dataset_ids = get_dataset_ids(client, MONGOD_HAZARD_DB, "TornadoDataset")

	dataset_ids = get_dataset_ids(client, MONGO_DATA_DB, "Dataset")

	if REMOVE_DATASET:
		# earthquake dataset
		if len(eq_dataset_ids) == 0:
			print("There is nothing in the earthquake dataset")
		else:
			print("Removing Earthquake Datasets")
			ep_url = rest_url + "hazard/api/earthquakes/"
			remove_dataset(ep_url, eq_dataset_ids)

		# earthquake model
		if len(eq_model_ids) == 0:
			print("There is nothing in the earthquake model")
		else:
			print("Removing Earthquake Models")
			ep_url = rest_url + "hazard/api/earthquakes/"
			remove_dataset(ep_url, eq_model_ids)

		# flood
		if len(flood_ids) == 0:
			print("There is nothing in the floods")
		else:
			print("Removing Floods")
			ep_url = rest_url + "hazard/api/floods/"
			remove_dataset(ep_url, flood_ids)

		# hurricane
		if len(hurricane_ids) == 0:
			print("There is nothing in the hurricanes")
		else:
			print("Removing Hurricanes")
			ep_url = rest_url + "hazard/api/hurricanes/"
			remove_dataset(ep_url, hurricane_ids)

		# hurricane windfields
		if len(hurricane_wf_ids) == 0:
			print("There is nothing in the hurricane windfields")
		else:
			print("Removing Hurricane Windfields")
			ep_url = rest_url + "hazard/api/hurricaneWindfields/"
			remove_dataset(ep_url, hurricane_wf_ids)

		# scenario earthquakes
		if len(scenario_eq_ids) == 0:
			print("There is nothing in the scenario earthquakes")
		else:
			print("Removing Scenario Earthquakes")
			ep_url = rest_url + "hazard/api/earthquakes/"
			remove_dataset(ep_url, scenario_eq_ids)

		# scenario tornado
		if len(scenario_tornado_ids) == 0:
			print("There is nothing in the scenario tornadoes")
		else:
			print("Removing Scenario Tornadoes")
			ep_url = rest_url + "hazard/api/tornadoes/"
			remove_dataset(ep_url, scenario_tornado_ids)

		# tornado dataset
		if len(tornado_dataset_ids) == 0:
			print("There is nothing in the tornado dataset")
		else:
			print("Removing Tornado Dataset")
			ep_url = rest_url + "hazard/api/tornadoes/"
			remove_dataset(ep_url, tornado_dataset_ids)

		# tornado model
		if len(tornado_model_ids) == 0:
			print("There is nothing in the tornado model")
		else:
			print("Removing Tornado Models")
			ep_url = rest_url + "hazard/api/earthquakes/"
			remove_dataset(ep_url, tornado_model_ids)

		# tsunami dataset
		if len(tsunami_dataset_ids) == 0:
			print("There is nothing in the tsunami datasets")
		else:
			print("Removing Tsunami Datasets")
			ep_url = rest_url + "hazard/api/tsunamis/"
			remove_dataset(ep_url, tsunami_dataset_ids)

		# regular dataset
		if len(dataset_ids) == 0:
			print("There is nothing in the regular datasets")
		else:
			print("Removing Regular Datasets")
			ep_url = rest_url + "data/api/datasets/"
			remove_dataset(ep_url, dataset_ids)

	if TUNNEL_NEEDED:
		server.stop()

def get_dataset_ids(client, db_name, coll_name):
	id_list = []

	# get hazard dataset ids
	db = client[db_name]
	db.collection = db[coll_name]
	result = db.collection.find({"creator": USER_NAME})

	for dictionary in result:
		doc = db.collection.find({'_id': dictionary["_id"]})
		for document in doc:
			# find out the object id and file name
			doc_id = document["_id"]
			id_list.append(str(doc_id))

	print(len(id_list))
	return id_list

def remove_dataset(rest_url, id_list):
	error_ids = []
	total = len(id_list)
	index = 0
	print(str(total) + " datasets will be removed")
	auth_token = 'Bearer ' + str(AUTH_TOKEN)
	for doc_id in id_list:
		delete_url = rest_url + doc_id
		response = requests.delete(delete_url, headers={'Authorization': auth_token})
		if response.status_code != 200:
			print("Failed to delete " + doc_id)
			error_ids.append(doc_id)
			pass
		index += 1
		left = total - index
		if left % 100 == 0:
			print(str(left) + " iterations left")

	print("failed to remove following ids")
	print(error_ids)


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




