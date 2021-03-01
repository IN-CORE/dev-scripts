"""
This script will update the bounding box information of the geodataset in the dataset db
check the cluster for local, dev, and prod
Set MONGO_USER and MONGO_KEYFILE
If you want to use tunnel to connect mongodb make TUNNEL_NEEDED to True
If you don't update db but just checking, make UPDATE_DB to False
"""

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
import requests
import zipfile36 as zipfile
import shutil
import tempfile
import fiona
import os
from osgeo import gdal

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_keyfile"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

ID_TOKEN = ""

UPDATE_DB = False
TUNNEL_NEEDED = False

#CLUSTER = "local"
# CLUSTER = "dev"
CLUSTER = "prod"

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
		mongo_user = ''
		mongo_password = ''
	if CLUSTER == "prod":
		rest_url = "https://incore.ncsa.illinois.edu/data/api/datasets/"
		mongo_host = '127.0.0.1'
		mongo_port = 27017
		mongo_user = ''
		mongo_password = ''

	if TUNNEL_NEEDED:
		server = get_mongo_server(mongo_host)
		server.start()

		client = MongoClient(MONGO_BIND_HOST, server.local_bind_port)  # server.local_bind_port is assigned local port
	else:
		client = MongoClient(mongo_host, 27017)
		client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_password, authSource='admin')
		print(client.server_info())

	db = client[MONGO_DB]
	db.collection = db["Dataset"]
	collection = db.collection

	result = db.Dataset.find()
	datasetDict = {}
	error_id = []

	for dictionary in result:
		doc = db.Dataset.find({'_id': dictionary["_id"]})
		for document in doc:
			if ("format" in document and "fileDescriptors" in document):
				# find out the object id and file name
				doc_id = document["_id"]
				object_id = str(doc_id)
				add_boundingbox = False
				if (document["format"] == 'shapefile' or document["format"] == 'raster'
						or document['format'] == 'geotiff' or document['format'] == 'geotif'):
					if ("boundingBox" in document):
						bounding_box = document['boundingBox']
						if bounding_box is None:
							print("Document has no bounding box informatoin " + object_id)
							add_boundingbox = True
					else:
						add_boundingbox = True

				if add_boundingbox:
					bbox = None
					down_url = rest_url + object_id + "/blob"

					for descriptors in document["fileDescriptors"]:
						filename = descriptors["filename"]
					if (document["format"] == 'shapefile'):
						filename = filename.split('.')[0]
						filename_full = filename + ".shp"
					else:
						fileext = filename.split('.')[1]
						if (fileext == 'asc'):
							is_asc = True
						filename_full = filename

					if UPDATE_DB:
						is_asc = False
						# create temp directory
						tmp_data_dir = tempfile.mkdtemp()
						down_filename = os.path.join(tmp_data_dir, (filename + ".zip"))

						# download dataset to temp directory
						print("Downlodaing the data for " + str(object_id))
						auth_token = 'Bearer ' + str(ID_TOKEN)

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
							except zipfile.BadZipfile as err:
								error_id.append(object_id)
								print("OS error: {0}".format(err))

							# read shapefile
							if (document["format"] == 'shapefile'):
								try:
									shape = fiona.open(os.path.join(tmp_data_dir, filename_full))
									bbox_col = shape.bounds
									bbox = [bbox_col[0], bbox_col[1], bbox_col[2], bbox_col[3]]
									shape.close()
								except IOError as err:
									print("IO error: {0}".format(err))
									error_id.append(object_id)
							if (document["format"] == 'raster' or document['format'] == 'geotiff' or document['format'] == 'geotif'):
								gdal.UseExceptions()
								if not is_asc:
									try:
										ds = gdal.Open(os.path.join(tmp_data_dir, filename_full))
										geo_trans = ds.GetGeoTransform()
										minx = geo_trans[0]
										maxy = geo_trans[3]
										maxx = minx + geo_trans[1] * ds.RasterXSize
										miny = maxy + geo_trans[5] * ds.RasterYSize
										bbox = [minx, miny, maxx, maxy]
										ds = None
									except RuntimeError as err:
										print("OS error: {0}".format(err))
										error_id.append(object_id)
							if bbox is not None:
								db.Dataset.update_one({'_id': doc_id}, {'$set': {"boundingBox": bbox}}, upsert=True)
								print("done updating db " + object_id)
						else:
							print("Unable to download " + str(object_id))
							print(str(response.status_code) + " " + str(response.text))
							error_id.append(str(object_id))

					# remove temp folder
					shutil.rmtree(tmp_data_dir)
	print(error_id)

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




