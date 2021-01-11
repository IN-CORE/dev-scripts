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
MONGO_USER = "ubuntu"
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "C:\\Users\\ywkim\\.ssh\\nist.pem"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

ID_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmNDlQdWF2UjdQRDB4MUhFdUdMSWhTYWJrazU0Z3FwYWx2WEx0cU56RlJ3In0.eyJqdGkiOiI4NTE5N2YzMS05ZjU5LTQ4MTgtODk0Ni1hYTJjN2YyZDdiZGIiLCJleHAiOjE2MTA0MTc1NjAsIm5iZiI6MCwiaWF0IjoxNjEwMzgxNTYwLCJpc3MiOiJodHRwczovL2luY29yZS1kZXYta3ViZS5uY3NhLmlsbGlub2lzLmVkdS9hdXRoL3JlYWxtcy9Jbi1jb3JlIiwic3ViIjoiZDY3ZGM3OTUtN2U1Ni00ZjE0LWEwMGQtMGY0ODYwM2Q4MWE3IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoicmVhY3QtYXV0aCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFmZDY4YWY1LTlhMjctNDM3Ni05YzYwLTA3YTNiMTViNjlkNyIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiaW5jb3JlX3VzZXJfcm9sZSJdfSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiWW9uZyBXb29rIEtpbSIsImdyb3VwcyI6WyJpbmNvcmVfYWRtaW4iLCJpbmNvcmVfanVweXRlciIsImluY29yZV9jb2UiLCJpbmNvcmVfdXNlciJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ5d2tpbSIsImdpdmVuX25hbWUiOiJZb25nIFdvb2siLCJmYW1pbHlfbmFtZSI6IktpbSIsImVtYWlsIjoieXdraW1AaWxsaW5vaXMuZWR1In0.bWJp1T4UyP5S8Zl6EG5Em5U3JqFDqpe8Uptj2gcoktV7m6yRc6jbW-995r_FDGLkyTmoeu3auSEKMkaMxBcoQE-oxGT5vxA89jw2kGJYeJsqsC4QW9o_FL6CZjj0UWQyHUeT2-VJxvKnTP2toNRDTA8PaLjdH45dk5HPRkbPe97XGDxKY_exBiNmjfidt3UoDgR3KyAR7P0NxdXcmG-i-i0bBt6uz3TlM3y75Co_w34hoRbXTV129zQOBasilv5xP93xtvREiC7e_cbviOSziE143n2MOYbhinZ86l10MbE-FfRsCErw0mbFCpi2iK76KmVhTqnyYEueim9tqS7rRg"
UPDATE_DB = True
TUNNEL_NEEDED = True

def main():
	# cluster = "local"
	cluster = "dev"
	# cluster = "prod"

	mongo_host = None
	rest_url = None

	if cluster == "local":
		mongo_host = "localhost"
		rest_url = "http://localhost:8080/data/api/datasets/"
	if cluster == "dev":
		mongo_host = "incore2-mongo-dev.ncsa.illinois.edu"
		rest_url = "https://incore-dev-kube.ncsa.illinois.edu/data/api/datasets/"
	if cluster == "prod":
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
				if ("boundingBox" in document):
					bounding_box = document['boundingBox']
					if bounding_box is None:
						print("Document has no bounding box informatoin " + object_id)
						add_boundingbox = True
				else:
					if (document["format"] == 'shapefile' or document["format"] == 'raster'
							or document['format'] == 'geotiff' or document['format'] == 'geotif'):
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
						# create temp directory
						tmp_data_dir = tempfile.mkdtemp()
						down_filename = os.path.join(tmp_data_dir, (filename + ".zip"))

						# download dataset to temp directory
						print("Downlodaing the data for " + str(object_id))
						auth_token = 'Bearer ' + str(ID_TOKEN)

						response = requests.get(down_url, headers={'Authorization': auth_token}, stream=True)
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
						if (document["format"] == 'raster'):
							gdal.UseExceptions()
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

						# remove temp folder
						shutil.rmtree(tmp_data_dir)
						db.Dataset.update_one({'_id': doc_id},
											  {'$set': {"boundingBox": bbox}}, upsert=False)
						print("done updatinb " + object_id)
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




