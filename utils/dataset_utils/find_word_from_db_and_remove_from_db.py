"""
This script will find a word that contains certain term from certain field
and will remove the dataset that contains the word from the database.
For example, if the dataset's title contains the word 'test,
then, the script will remove the dataset that contains the word 'test' from title
and will remove it using the rest end point.
check the cluster for local, dev, and prod
Set MONGO_USER and MONGO_KEYFILE
If you want to use tunnel to connect mongodb make TUNNEL_NEEDED to True
"""
import re
import requests

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

UPDATE_DB = False
TUNNEL_NEEDED = True

# CLUSTER = "local"
# CLUSTER = "dev"
CLUSTER = "prod"

AUTH_TOKEN = ""

def main():
	mongo_host = None
	rest_url = None
	error_ids = []

	if CLUSTER == "local":
		mongo_host = "localhost"
		rest_url = "http://localhost:8080/data/api/datasets/"
	elif CLUSTER == "dev":
		mongo_host = "incore2-mongo-dev.ncsa.illinois.edu"
		rest_url = "https://incore-dev-kube.ncsa.illinois.edu/data/api/datasets/"
	elif CLUSTER == "prod":
		mongo_host = "incore2-mongo1.ncsa.illinois.edu"
		rest_url = "https://incore.ncsa.illinois.edu/data/api/datasets/"

	if TUNNEL_NEEDED:
		server = get_mongo_server(mongo_host)
		server.start()
		client = MongoClient(MONGO_BIND_HOST, server.local_bind_port)  # server.local_bind_port is assigned local port
	else:
		client = MongoClient(mongo_host, 27017)

	db = client[MONGO_DB]
	db.collection = db["Dataset"]

	# TODO put the word to find in the following line
	rgx = re.compile('.*test.*', re.IGNORECASE)  # compile the regex
	field_to_find = "title"
	result = db.Dataset.find({field_to_find: rgx})

	for dictionary in result:
		is_nbsr = False
		doc = db.Dataset.find({'_id': dictionary["_id"]})
		for document in doc:
			doc_id = document["_id"]

			# check if title contains the word 'nbsr' and if so, don't delete it
			dataset_title = document["title"]
			if "nbsr" in dataset_title.lower():
				is_nbsr = True

		if is_nbsr:
			print(str(doc_id) + " is nbsr, not deleting.")
		else:
			print("Deleting " + str(doc_id))
			delete_url = rest_url + str(doc_id)
			auth_token = 'Bearer ' + str(AUTH_TOKEN)
			response = requests.delete(delete_url, headers={'Authorization': auth_token})
			if response.status_code == 200:
				print(str(doc_id) + " deleted.")
			else:
				print("Failed to delete " + str(doc_id))
				error_ids.append(doc_id)

	print(error_ids)

	if TUNNEL_NEEDED:
		server.stop()

	print("Done")

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




