from pymongo import MongoClient

def update_path(path):
	newPath = (path.split("file:/home/incore/data"))
	if len(newPath) == 1:
		print("error converting " + path)
		return path
	print (newPath[1])
	return (newPath[1])

client = MongoClient("incore2-mongo1.ncsa.illinois.edu", 27017)

db = client.datadb

result = db.Dataset.find()

datasetDict = {}

for dictionary in result:
	#improve this line
	doc = db.Dataset.find({'_id':dictionary["_id"]})
	for fileDescriptor in doc:
		if("fileDescriptors" in fileDescriptor):
			fileDescriptorDict = {}
			descriptorID = fileDescriptor["_id"]
			for descriptors in fileDescriptor["fileDescriptors"]:
				fileDescriptorDict[descriptors["_id"]] = descriptors["dataURL"]
			datasetDict[dictionary["_id"]] = fileDescriptorDict


updatedDatasetDict = {}

for k,fileDescritor in datasetDict.items():
	# update all paths
	updatedfileDescriptorDict = {}
	for _id, path in fileDescritor.items():
		path = update_path(path)
		updatedfileDescriptorDict[_id] = path
	updatedDatasetDict[k] = updatedfileDescriptorDict

#write paths into db
for docIds, descriptors in updatedDatasetDict.items():
	for id, path in descriptors.items():
		db.Dataset.update_one({'_id':docIds,'fileDescriptors._id':id}, {'$set':{"fileDescriptors.$.dataURL":path}}, upsert=False)


client.close()