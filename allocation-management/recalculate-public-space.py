from bson import ObjectId
from pymongo import MongoClient

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT FORGET TO MAKE A BACK UP OF THE DATABASE BEFORE PERFORMING THIS SCRIPT!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

This scripts should be run after running the update_owner.py script first

To run this, you need to port forward kube cluster's mongodb to your local mongodb
For example, in dev-cluster, you want to forward the kube cluster's port to your local's 27019,
do 
1. kubectl config use-context incore-dev
2. kubectl port-forward -n incore services/incore-mongodb 27019:27017
Then, the mongodb in dev cluster is forwarded to the port 27019 in your local. 
In the code, change mongo_port variable to 27019, and put the mongodb user and password 
in the code and run the script.

The code is doing
1. connect to space mongodb depository
2. set the public space id
3. grab the information of the id list
4. iterate each ids in id list
5. set each dataset id's ownership to public id's name
6. recalculate the quota by reducing the dataset number and dataset size

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT FORGET TO MAKE A BACK UP OF THE DATABASE BEFORE PERFORMING THIS SCRIPT!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


def main(public_id_dict):
    mongo_host = "127.0.0.1"
    mongo_port = 27018
    mongo_user = 'root'
    mongo_password = ''

    client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_password, authSource='admin')
    # use this for local test
    # client = MongoClient("localhost", 27017, authSource='admin')
    print(client.server_info())

    # query member list
    members = get_member_list(client, public_id_dict)

    if len(members) == 0:
        print("There is no result.")
    else:
        # update the owner name in each datasets
        for member in members:
            print("querying id: ", member)

            # find it from data db
            is_data = query_from_datadb(client, member)

            if not is_data:
                # find it from dfr3 db
                is_dfr3 = query_from_dfr3db(client, member)

                if not is_dfr3:
                    # find it from hazard db
                    is_hazard = query_from_hazarddb(client, member)

                    if not is_hazard:
                        print("The member id: " + member + " doesn't exist in the db")


def query_from_datadb(client, member):
    db = client["datadb"]
    db.collection = db["Dataset"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("dataset")
        return True

    print("Not dataset")
    return False


def query_from_dfr3db(client, member):
    db = client["dfr3db"]

    # check fragility set
    db.collection = db["FragilitySet"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("fragility")
        return True

    # check mapping set
    db.collection = db["MappingSet"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("mapping")
        return True

    # check repair set
    db.collection = db["RepairSet"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("repair")
        return True

    # check restoration set
    db.collection = db["RestorationSet"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("restoration")
        return True

    print("Not dfr3")
    return False


def query_from_hazarddb(client, member):
    db = client["hazarddb"]

    # earthquake dataset
    db.collection = db["EarthquakeDataset"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("Earthquake dataset")
        return True

    # earthquake model
    db.collection = db["EarthquakeModel"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("Earthquake model")
        return True

    # hurricane windfields
    db.collection = db["HurricaneWindfields"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("Hurricane windfields")
        return True

    # tornado dataset
    db.collection = db["TornadoDataset"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("Tornado dataset")
        return True

    # tornado model
    db.collection = db["TornadoModel"]
    oid = ObjectId(member)
    doc = db.collection.find({"_id": oid})

    if len(list(doc)) > 0:
        print("Tornado Model")
        return True

    print("Not hazard dataset")
    return False


def get_member_list(client, public_id_dict):
    db = client["spacedb"]
    db.collection = db["Space"]
    members = None

    doc = db.collection.find({'privileges.userPrivileges': public_id_dict})

    # you have to iterate right after, otherwise, the aliveness of doc will be false
    for doc_size, document in enumerate(doc):
        # find out the object id and file name
        doc_id = document["_id"]
        members = document["members"]
    doc_size = doc_size + 1

    if doc_size== 0:
        print("There is no record for public id... Aborting...")
        return []

    if doc_size > 1:
        print("There are more than one records for public id... Aborting...")
        return []

    return members



    # id_list = []
    # title_list = []
    # author_list = []
    # date_list = []
    # space_list = []
    # error_reason_list = []
    #
    # for dictionary in result:
    # 	doc = db.Dataset.find({'_id': dictionary["_id"]})
    # 	for document in doc:
    # 		# find out the object id and file name
    # 		doc_id = document["_id"]
    # 		object_id = str(doc_id)
    #
    # 		if ("format" in document):
    # 			if (document["format"].lower() == "shapefile"):
    # 				# print("Shapefile dataset " + str(object_id))
    # 				if not("fileDescriptors" in document):
    # 					print("There is no files attached to the dataset")
    # 					error_reason = "No files attached to the dataset"
    #
    # 					# construct lists
    # 					id_list.append(str(object_id))
    # 					error_reason_list.append(error_reason)
    # 					if ("titie" in document):
    # 						title_list.append(document["title"])
    # 					else:
    # 						title_list.append("no title")
    # 					if ("creator" in document):
    # 						author_list.append(document["creator"])
    # 					else:
    # 						author_list.append("no creator")
    # 					if ("date" in document):
    # 						date_list.append(document["date"])
    # 					else:
    # 						date_list.append("no date")
    # 					if ("space" in document):
    # 						space_list.append(document["space"])
    # 					else:
    # 						space_list.append("no space")
    # 				else:
    # 					# find out dataset's format
    # 					dataset_format = document['format']
    # 					error_reason = "Missing"
    #
    # 					# find out file extension
    # 					is_shp = False
    # 					is_shx = False
    # 					is_dbf = False
    # 					is_prj = False
    #
    # 					for descriptors in document["fileDescriptors"]:
    # 						filename = descriptors["filename"]
    # 						fileext = filename.split('.')[1]
    # 						if (fileext.lower() == 'shp'):
    # 							is_shp = True
    # 						if (fileext.lower() == 'shx'):
    # 							is_shx = True
    # 						if (fileext.lower() == 'dbf'):
    # 							is_dbf = True
    # 						if (fileext.lower() == 'prj'):
    # 							is_prj = True
    #
    # 					if not is_shp:
    # 						error_reason = error_reason + " shp"
    # 						# print("    shp file is missing")
    # 					if not is_shx:
    # 						error_reason = error_reason + " shx"
    # 						# print("    shx file is missing")
    # 					if not is_dbf:
    # 						error_reason = error_reason + " dbf"
    # 						# print("    dbf file is missing")
    # 					if not is_prj:
    # 						error_reason = error_reason + " prj"
    # 						# print("    prj file is missing")
    #
    # 					# construct lists
    # 					if is_shp and is_shx and is_dbf and is_prj:
    # 						pass
    # 					else:
    # 						print(error_reason)
    # 						id_list.append(str(object_id))
    # 						error_reason_list.append(error_reason)
    # 						if ("titie" in document):
    # 							title_list.append(document["title"])
    # 						else:
    # 							title_list.append("no title")
    # 						if ("creator" in document):
    # 							author_list.append(document["creator"])
    # 						else:
    # 							author_list.append("no creator")
    # 						if ("date" in document):
    # 							date_list.append(document["date"])
    # 						else:
    # 							date_list.append("no date")
    # 						if ("space" in document):
    # 							space_list.append(document["space"])
    # 						else:
    # 							space_list.append("no space")
    #
    # print("ID, Title, Creator, Date, Reason")
    # for dataset_id, title, creator, date, reason \
    # 		in zip(id_list, title_list, author_list, date_list, error_reason_list):
    # 	print(str(dataset_id) + "," + title + "," + creator + "," + str(date) + "," + reason)
    #
    # if REMOVE_DATASET:
    # 	print("Starting remove process")
    # 	error_ids = []
    # 	for doc_id in id_list:
    # 		delete_url = rest_url + str(doc_id)
    # 		auth_token = 'Bearer ' + str(AUTH_TOKEN)
    # 		response = requests.delete(delete_url, headers={'Authorization': auth_token})
    # 		if response.status_code == 200:
    # 			print(str(doc_id) + " deleted.")
    # 		else:
    # 			print("Failed to delete " + str(doc_id))
    # 			error_ids.append(doc_id)
    # 			pass
    #
    # 	print(error_ids)


if __name__ == "__main__":
    # change this for getting the public id
    public_id_dict = {"ergo": "ADMIN"}
    main(public_id_dict)
