from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
import requests
import zipfile36 as zipfile
import shutil
import tempfile
import fiona
from osgeo import gdal

MONGO_DB = "datadb"
MONGO_USER = ""
MONGO_PASS = "PASSWORD"
MONGO_KEYFILE = "path_to_key_file"
MONGO_BIND_HOST = "127.0.0.1"
MONGO_BIND_PORT = 27017

ID_TOKEN = ""
UPDATE_DB = False
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
						down_filename = tmp_data_dir + '\\' + filename + ".zip"

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
								shape = fiona.open(tmp_data_dir + '\\' + filename_full)
								bbox_col = shape.bounds
								bbox = [bbox_col[0], bbox_col[1], bbox_col[2], bbox_col[3]]
								shape.close()
							except IOError as err:
								print("IO error: {0}".format(err))
								error_id.append(object_id)
						if (document["format"] == 'raster'):
							gdal.UseExceptions()
							try:
								ds = gdal.Open(tmp_data_dir + '\\' + filename_full)
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




