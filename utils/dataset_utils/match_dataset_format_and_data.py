"""
This script will scan and match the geodataset's format
For example, if the dataset's format is shape but the file in FileDescritpor is 'tif'
then, it will change the dataset's format as 'geotif'
This script will change format of the dataset based on File extension
check the cluster for local, dev, and prod
Set MONGO_USER and MONGO_KEYFILE
If you want to use tunnel to connect mongodb make TUNNEL_NEEDED to True
"""

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_your_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

CLUSTER = "local"
# CLUSTER = "dev"
# CLUSTER = "prod"
UPDATE_DB = False
TUNNEL_NEEDED = False


def main():
	mongo_host = None
	rest_url = None

	if CLUSTER == "local":
		mongo_host = "localhost"
	if CLUSTER == "dev":
		mongo_host = "incore2-mongo-dev.ncsa.illinois.edu"
	if CLUSTER == "prod":
		mongo_host = "incore2-mongo1.ncsa.illinois.edu"

	if TUNNEL_NEEDED:
		server = get_mongo_server(mongo_host)
		server.start()

		client = MongoClient(MONGO_BIND_HOST, server.local_bind_port)  # server.local_bind_port is assigned local port
	else:
		client = MongoClient(mongo_host, 27017)

	db = client[MONGO_DB]
	db.collection = db["Dataset"]

	result = db.Dataset.find()

	for dictionary in result:
		doc = db.Dataset.find({'_id': dictionary["_id"]})
		for document in doc:
			if ("format" in document and "fileDescriptors" in document):
				# find out the object id and file name
				doc_id = document["_id"]
				object_id = str(doc_id)

				# find out dataset's format
				dataset_format = document['format']

				# find out file extension
				is_asc = False
				is_shapefile = False
				is_tif = False

				for descriptors in document["fileDescriptors"]:
					filename = descriptors["filename"]
					fileext = filename.split('.')[1]
					if (fileext == 'asc'):
						is_asc = True
					if (fileext == 'shp'):
						is_shapefile = True
					if (fileext == 'tif'):
						is_tif = True

				if is_asc:
					if dataset_format != "raster":
						print(str(doc_id) + " The file is asc but the dataset format is not " + dataset_format)
						if UPDATE_DB:
							db.Dataset.update_one({'_id': doc_id}, {'$set': {"format": "raster"}}, upsert=False)
							print("done updatinb " + object_id)
				if is_shapefile:
					# need to exclude network
					# if dataset_format.lower() == "network":
					# 	print(str(doc_id) + " The dataset format is Network, skip")
					# else:
					if dataset_format != "shapefile":
						print(str(doc_id) + " The file is shapefile but the dataset format is " + dataset_format)
						if UPDATE_DB:
							db.Dataset.update_one({'_id': doc_id}, {'$set': {"format": "shapefile"}}, upsert=False)
							print("done updatinb " + object_id)
				if is_tif:
					if dataset_format != "geotif" and dataset_format != "geotiff":
						print(str(doc_id) + " The file is tif but the dataset format is " + dataset_format)
						if UPDATE_DB:
							db.Dataset.update_one({'_id': doc_id}, {'$set': {"format": "geotif"}}, upsert=False)
							print("done updatinb " + object_id)
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




