from bson import ObjectId
from pymongo import MongoClient

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT FORGET TO MAKE A BACK UP OF THE DATABASE BEFORE PERFORMING THIS SCRIPT!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

To run this, you need to port forward kube cluster's mongodb to your local mongodb
For example, in dev-cluster, you want to forward the kube cluster's port to your local's 27019,
do 
1. kubectl config use-context incore-dev
2. kubectl port-forward -n incore services/incore-mongodb 27019:27017
Then, the mongodb in dev cluster is forwarded to the port 27019 in your local. 
In the code, change mongo_port variable to 27019, and put the mongodb user and password 
in the code and run the script.

The script is doing
1. check dataset
2. check dfr3
3. check hazard
4. check if there is owner item in the dataset
5. if not, create an owner item with the same values as creator

You can only check the status instead of actually updating the database first and it is recommended
To do that, set the variable just_check to true.
If just_check variable is false, it will update the database

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT FORGET TO MAKE A BACK UP OF THE DATABASE BEFORE PERFORMING THIS SCRIPT!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


def main():
    just_check = True
    mongo_host = "127.0.0.1"
    mongo_port = 27019
    mongo_user = 'root'
    mongo_password = 'password'

    client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_password, authSource='admin')
    # use this for local test
    # client = MongoClient("localhost", 27017, authSource='admin')

    print(client.server_info())

    db_data = "datadb"
    db_dfr3 = "dfr3db"
    db_hazard = "hazarddb"
    update_owner_indb(client, db_data, "Dataset", just_check)
    update_owner_indb(client, db_dfr3, "FragilitySet", just_check)
    update_owner_indb(client, db_dfr3, "MappingSet", just_check)
    update_owner_indb(client, db_dfr3, "RepairSet", just_check)
    update_owner_indb(client, db_dfr3, "RestorationSet", just_check)
    update_owner_indb(client, db_hazard, "EarthquakeDataset", just_check)
    update_owner_indb(client, db_hazard, "EarthquakeModel", just_check)
    update_owner_indb(client, db_hazard, "FloodDataset", just_check)
    update_owner_indb(client, db_hazard, "HurricaneDataset", just_check)
    update_owner_indb(client, db_hazard, "HurricaneWindfields", just_check)
    update_owner_indb(client, db_hazard, "ScenarioEarthquake", just_check)
    update_owner_indb(client, db_hazard, "ScenarioTornado", just_check)
    update_owner_indb(client, db_hazard, "TornadoDataset", just_check)
    update_owner_indb(client, db_hazard, "TornadoModel", just_check)
    update_owner_indb(client, db_hazard, "TsunamiDataset", just_check)


def update_owner_indb(client, db_name, col_name, just_check):
    db = client[db_name]
    db.collection = db[col_name]
    doc = db.collection.find()

    if len(list(doc)) == 0:
        print("Error: There is no entries in the given db")
        return

    for document in db.collection.find():
        doc_id = document["_id"]
        is_creator = True
        is_owner = True

        # check if there is creator
        try:
            creator = document["creator"]
        except KeyError:
            # there are some hazards that doesn't have creator
            # mostly the user should be ergo
            creator = "ergo"
            is_creator = False

        # check if there is owner
        try:
            owner = document["owner"]
        except KeyError:
            is_owner = False

        # update creator
        if not is_creator:
            if just_check:
                print("Checking: Updating creator for " + db_name + " " + col_name + " " + str(doc_id))
            else:
                print("Updating creator for " + db_name + " " + col_name + " " + str(doc_id))
                db.collection.update_one({
                    '_id': doc_id
                }, {
                    '$set': {
                        'creator': creator
                    }
                }, upsert=False)

        # update owner
        if not is_owner:
            if just_check:
                print("Checking: Updating owner for " + db_name + " " + col_name + " " + str(doc_id))
            else:
                print("Updating owner for " + db_name + " " + col_name + " " + str(doc_id))
                db.collection.update_one({
                    '_id': doc_id
                }, {
                    '$set': {
                        'owner': creator
                    }
                }, upsert=False)


if __name__ == "__main__":
    main()
