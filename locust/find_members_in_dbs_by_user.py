# this script will find out the hazard created by given user
# and update the space with the list of new members from the selected databases
# this script is incomplete that it only scand datadb, earthquake dataset, tornado model
# you should be able to add more databases and collections by copying the methods

################################################################
# set the user at the very end of this script
################################################################

from bson import ObjectId
from pymongo import MongoClient
import copy


def main(user_dict):
    mongo_host = "127.0.0.1"
    # set this to what ever your forwarded from kube mongodb
    # you can do this by
    # kubectl config use-context incore-dev (prod)
    # kubectl port-forward -n incore services/mongodb 27020:27017
    mongo_port = 27020
    mongo_user = 'root'
    # give proper password
    ################################################################
    ################################################################
    ################################################################
    # DO NOT PUT YOUR PASSWORD IN THE CODE and PUSH to the repo
    mongo_password = 'password'
    ################################################################
    ################################################################
    ################################################################

    client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_password, authSource='admin')
    # use this for local test
    # client = MongoClient("localhost", 27017, authSource='admin')
    print(client.server_info())


    # check what database you want to use
    is_data = False
    is_dfr3 = False
    is_earthquake_dataset = True
    is_hurricane = False
    is_tornado_model = True
    is_flood = False

    # query user's space id
    space_dict = {"metadata.name": user_dict["creator"]}
    space_list = query_user_space_id(client, space_dict)
    space_id = space_list[0]["_id"]
    existing_members = get_member_list(client, space_dict)
    merged_list = copy.copy(existing_members)

    if is_data:
        doc_list = query_from_earthquake_dataset(client, user_dict)
        id_list = []
        if doc_list is None:
            print("No dataset")
            return None
        else:
            for doc in doc_list:
                doc_id = str(doc['_id'])
                id_list.append(doc_id)
            merged_list = merge_with_existing_members(merged_list, id_list)

    if is_earthquake_dataset:
        doc_list = query_from_earthquake_dataset(client, user_dict)
        id_list = []
        if doc_list is None:
            print("No dataset")
            return
        else:
            for doc in doc_list:
                doc_id = str(doc['_id'])
                id_list.append(doc_id)
            merged_list = merge_with_existing_members(merged_list, id_list)

    if is_tornado_model:
        doc_list = query_from_tornado_model(client, user_dict)
        id_list = []
        if doc_list is None:
            print("No dataset")
            return
        else:
            for doc in doc_list:
                doc_id = str(doc['_id'])
                id_list.append(doc_id)
            merged_list = merge_with_existing_members(merged_list, id_list)

    # for member in merged_list:
    #     print(member)

    # Update the space using the merged list
    db = client["spacedb"]
    db.collection = db["Space"]
    db.collection.update_one({"_id": space_id}, {"$set": {"members": merged_list}})

    print("Updated the space with the merged list")


def merge_with_existing_members(existing_list, id_list):
    # Merge and remove duplicates
    merged_list = list(set(existing_list + id_list))

    return merged_list


def get_member_list(client, id_dict):
    db = client["spacedb"]
    db.collection = db["Space"]
    members = None

    doc = db.collection.find(id_dict)

    # you have to iterate right after, otherwise, the aliveness of doc will be false
    for doc_size, document in enumerate(doc):
        # find out the object id and file name
        doc_id = document["_id"]
        members = document["members"]
        doc_size = doc_size + 1

    if doc_size == 0:
        print("There is no record for public id... Aborting...")
        return []

    if doc_size > 1:
        print("There are more than one records for public id... Aborting...")
        return []

    return members


def query_user_space_id(client, user_dict):
    db = client["spacedb"]
    db.collection = db["Space"]
    doc = db.collection.find(user_dict)

    doc_list = list(doc)
    if len(doc_list) > 0:
        return doc_list
    else:
        return None


def query_from_datadb(client, user_dict):
    db = client["datadb"]
    db.collection = db["Dataset"]
    doc = db.collection.find(user_dict)

    doc_list = list(doc)
    if len(doc_list) > 0:
        return doc_list
    else:
        return None


def query_from_earthquake_dataset(client, user_dict):
    db = client["hazarddb"]
    db.collection = db["EarthquakeDataset"]
    doc = db.collection.find(user_dict)

    doc_list = list(doc)
    if len(doc_list) > 0:
        return doc_list
    else:
        return None


def query_from_tornado_model(client, user_dict):
    db = client["hazarddb"]
    db.collection = db["TornadoModel"]
    doc = db.collection.find(user_dict)

    doc_list = list(doc)
    if len(doc_list) > 0:
        return doc_list
    else:
        return None
    doc = db.collection.find(user_dict)

    doc_list = list(doc)
    if len(doc_list) > 0:
        return doc_list
    else:
        return None


if __name__ == "__main__":
    # change this for getting the public id
    public_id_dict = {"creator": "ylyang"}
    main(public_id_dict)
