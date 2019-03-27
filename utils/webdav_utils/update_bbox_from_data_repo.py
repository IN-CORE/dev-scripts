from pymongo import MongoClient
import requests
import zipfile36 as zipfile
import shutil
import tempfile
import fiona
from osgeo import gdal

def main():
	# client = MongoClient("localhost", 27017)
	client = MongoClient("incore2-mongo1.ncsa.illinois.edu", 27017)
	db = client.datadb
	result = db.Dataset.find()
	datasetDict = {}
	rest_url = "http://incore2-services.ncsa.illinois.edu:8888/data/api/datasets/"
	# rest_url = "http://localhost:8080/data/api/datasets/"
	error_id = []

	for dictionary in result:
		doc = db.Dataset.find({'_id': dictionary["_id"]})
		for document in doc:
			if ("format" in document and "fileDescriptors" in document):
				# find out the object id and file name
				doc_id = document["_id"]
				object_id = str(doc_id)
				if ("boundingBox" in document):
					print("this document already has bounding box information: " + object_id)
				else:
					if (document["format"] == 'shapefile' or document["format"] == 'raster'):
					# if (document["format"] == 'raster'):
						bbox = None
						down_url = rest_url + object_id + "/blob"
						print(object_id)
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

						# create temp directory
						tmp_data_dir = tempfile.mkdtemp()
						down_filename = tmp_data_dir + '\\' + filename + ".zip"

						# download dataset to temp directory
						response = requests.get(down_url, headers={"X-Credential-Username":"ywkim"}, stream=True)
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
						print("done")
	print(error_id)

if __name__ == "__main__":
	main()




