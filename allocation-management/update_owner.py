from bson import ObjectId
from pymongo import MongoClient

"""
1. check dataset
2. check dfr3
3. check hazard
4. check if there is owner item in the dataset
5. if not, create an owner item with the same values as creator
"""

def main():
    mongo_host = "127.0.0.1"
    mongo_port = 27020
    mongo_user = 'root'
    mongo_password = ''

    client = MongoClient(mongo_host, mongo_port, username=mongo_user, password=mongo_password, authSource='admin')
    # use this for local test
    # client = MongoClient("localhost", 27017, authSource='admin')

    print(client.server_info())

    db_data = "datadb"
    db_dfr3 = "dfr3db"
    db_hazard = "hazarddb"
    update_owner_indb(client, db_data, "Dataset")
    update_owner_indb(client, db_dfr3, "FragilitySet")
    update_owner_indb(client, db_dfr3, "MappingSet")
    update_owner_indb(client, db_dfr3, "RepairSet")
    update_owner_indb(client, db_dfr3, "RestorationSet")
    update_owner_indb(client, db_hazard, "EarthquakeDataset")
    update_owner_indb(client, db_hazard, "EarthquakeModel")
    update_owner_indb(client, db_hazard, "FloodDataset")
    update_owner_indb(client, db_hazard, "HurricaneDataset")
    update_owner_indb(client, db_hazard, "HurricaneWindfields")
    update_owner_indb(client, db_hazard, "ScenarioEarthquake")
    update_owner_indb(client, db_hazard, "ScenarioTornado")
    update_owner_indb(client, db_hazard, "TornadoDataset")
    update_owner_indb(client, db_hazard, "TornadoModel")
    update_owner_indb(client, db_hazard, "TsunamiDataset")



def update_owner_indb(client, db_name, col_name):
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
            # print("Updating creator for " + db_name + " " + col_name + " " + str(doc_id))
            print(db_name + " " + col_name + " " + str(doc_id))
            # db.collection.update_one({
            #     '_id': doc_id
            # }, {
            #     '$set': {
            #         'creator': creator
            #     }
            # }, upsert=False)

        # # update owner
        # if not is_owner:
        #     print("Updating owner for " + db_name + " " + col_name + " " + str(doc_id))
        #     db.collection.update_one({
        #         '_id': doc_id
        #     }, {
        #         '$set': {
        #             'owner': creator
        #         }
        #     }, upsert=False)


if __name__ == "__main__":
    main()