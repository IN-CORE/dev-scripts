"""
This script will scan and check if the shapefile dataset format is actually shapefile
and all the shapefile component, 'prj', 'dbf', 'shx', and 'shp' are in there.
For example, if the dataset's format is shape but the file in FileDescritpor has only 'shp',
then, it should be removed.
Set MONGO_USER and MONGO_KEYFILE
If you want to use tunnel to connect mongodb make TUNNEL_NEEDED to True
"""
import requests

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

#CLUSTER = "local"
CLUSTER = "dev"
#CLUSTER = "prod"

REMOVE_DATASET = False
TUNNEL_NEEDED = True

AUTH_TOKEN = ""


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

	id_list = []
	title_list = []
	author_list = []
	date_list = []
	space_list = []
	error_reason_list = []

	for dictionary in result:
		doc = db.Dataset.find({'_id': dictionary["_id"]})
		for document in doc:
			# find out the object id and file name
			doc_id = document["_id"]
			object_id = str(doc_id)

			if ("format" in document):
				if (document["format"].lower() == "shapefile"):
					# print("Shapefile dataset " + str(object_id))
					if not("fileDescriptors" in document):
						print("There is no files attached to the dataset")
						error_reason = "No files attached to the dataset"

						# construct lists
						id_list.append(str(object_id))
						error_reason_list.append(error_reason)
						if ("titie" in document):
							title_list.append(document["title"])
						else:
							title_list.append("no title")
						if ("creator" in document):
							author_list.append(document["creator"])
						else:
							author_list.append("no creator")
						if ("date" in document):
							date_list.append(document["date"])
						else:
							date_list.append("no date")
						if ("space" in document):
							space_list.append(document["space"])
						else:
							space_list.append("no space")
					else:
						# find out dataset's format
						dataset_format = document['format']
						error_reason = "Missing"

						# find out file extension
						is_shp = False
						is_shx = False
						is_dbf = False
						is_prj = False

						for descriptors in document["fileDescriptors"]:
							filename = descriptors["filename"]
							fileext = filename.split('.')[1]
							if (fileext.lower() == 'shp'):
								is_shp = True
							if (fileext.lower() == 'shx'):
								is_shx = True
							if (fileext.lower() == 'dbf'):
								is_dbf = True
							if (fileext.lower() == 'prj'):
								is_prj = True

						if not is_shp:
							error_reason = error_reason + " shp"
							# print("    shp file is missing")
						if not is_shx:
							error_reason = error_reason + " shx"
							# print("    shx file is missing")
						if not is_dbf:
							error_reason = error_reason + " dbf"
							# print("    dbf file is missing")
						if not is_prj:
							error_reason = error_reason + " prj"
							# print("    prj file is missing")

						# construct lists
						if is_shp and is_shx and is_dbf and is_prj:
							pass
						else:
							print(error_reason)
							id_list.append(str(object_id))
							error_reason_list.append(error_reason)
							if ("titie" in document):
								title_list.append(document["title"])
							else:
								title_list.append("no title")
							if ("creator" in document):
								author_list.append(document["creator"])
							else:
								author_list.append("no creator")
							if ("date" in document):
								date_list.append(document["date"])
							else:
								date_list.append("no date")
							if ("space" in document):
								space_list.append(document["space"])
							else:
								space_list.append("no space")

	print("ID, Title, Creator, Date, Reason")
	for dataset_id, title, creator, date, reason \
			in zip(id_list, title_list, author_list, date_list, error_reason_list):
		print(str(dataset_id) + "," + title + "," + creator + "," + str(date) + "," + reason)

	if REMOVE_DATASET:
		print("Starting remove process")
		error_ids = []
		for doc_id in id_list:
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




