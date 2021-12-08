""""
This scripts adds the each users data/hazard/dfr3 usage status to space
The scripts directly access the all the databases instead of using usage endpoint api,
since the usage endpoint api doesn't have an ability to generate all the user id,
unless when the proper auth token for each user is provide, which is not possible.

To run this script for each cluster, not local,
you HAVE TO DO PORT FORWARDING that points to the mongodb of the cluster.
"""
from pymongo import MongoClient

DATA_TYPE_HAZARD = ["ergo:probabilisticEarthquakeRaster", "ergo:deterministicEarthquakeRaster",
                    "incore:probabilisticTsunamiRaster", "incore:deterministicTsunamiRaster",
                    "incore:probabilisticHurricaneRaster", "incore:deterministicHurricaneRaster",
                    "incore:hurricaneGridSnapshot", "incore:tornadoWindfield",
                    "incore:deterministicFloodRaster", "incore:probabilisticFloodRaster",
                    "ergo:hazardRaster"]


def update_space_base_allocation_information():
    # set parameters
    auth_needed = False
    mongo_username = "admin"
    mongo_password = ""
    host = "localhost"
    port = "27017"

    # run process
    if auth_needed:
        client = MongoClient('mongodb://%s:%s@%s:%s' % (mongo_username, mongo_password, host, port))
    else:
        client = MongoClient('mongodb://%s:%s' % (host, port))

    # database
    db_data = client["datadb"]
    db_dfr3 = client["dfr3db"]
    db_hazard = client["hazarddb"]
    db_space = client["spacedb"]

    # data collections
    coll_data = db_data["Dataset"]

    # dfr3 collections
    coll_f = db_dfr3["FragilitySet"]
    coll_m = db_dfr3["MappingSet"]
    coll_r = db_dfr3["RepairSet"]

    # hazard collections
    coll_ed = db_hazard["EarthquakeDataset"]
    coll_em = db_hazard["EarthquakeModel"]
    coll_fd = db_hazard["FloodDataset"]
    coll_hd = db_hazard["HurricaneDataset"]
    coll_hw = db_hazard["HurricaneWindfields"]
    coll_se = db_hazard["ScenarioEarthquake"]
    coll_st = db_hazard["ScenarioTornado"]
    coll_td = db_hazard["TornadoDataset"]
    coll_tm = db_hazard["TornadoModel"]
    coll_tsd = db_hazard["TsunamiDataset"]

    # space collections
    coll_space = db_space["Space"]

    #
    db_space_docs = coll_space.find({})
    space_doc_list = list(db_space_docs)

    # check if it is user space or group space
    for doc in space_doc_list:
        doc_id = doc["_id"]
        if 'privileges' in doc:
            privileges = doc["privileges"]
            if 'groupPrivileges' in privileges:
                # update group space
                update_group_data(doc_id, doc)
            else:
                # update user space
                user_name = doc["metadata"]["name"]
                num_dataset, file_size = query_datadb_status(coll_data, user_name, "dataset")
                num_hazard_dataset, hazard_file_size = query_datadb_status(coll_data, user_name, "hazard")
                num_hazard = query_hazard_count(user_name, coll_ed, coll_em, coll_fd, coll_hd, coll_hw, coll_se,
                                                coll_st, coll_td, coll_tm, coll_tsd)
                num_dfr3 = query_dfr3_count(user_name, coll_f, coll_m, coll_r)
                update_usage_info(doc_id, coll_space, user_name, num_dataset, num_hazard_dataset,
                                  num_hazard, num_dfr3, file_size, hazard_file_size)
                # print(user_name, num_dataset, num_hazard_dataset, num_hazard, num_dfr3, file_size, hazard_file_size)


def query_test(collection, creator):
    query = dict()
    query_parts = [{'creator': creator}, {'dataType': {'$in': DATA_TYPE_HAZARD}}]
    query['$and'] = query_parts
    db_data = collection.find(query)
    data_list = list(db_data)
    print(len(data_list))
    print(data_list)


def query_hazard_count(username, coll_ed, coll_em, coll_fd, coll_hd, coll_hw,
                       coll_se, coll_st, coll_td, coll_tm, coll_tsd):
    num_ed = get_count_by_creator(coll_ed, username)
    num_em = get_count_by_creator(coll_em, username)
    num_fd = get_count_by_creator(coll_fd, username)
    num_hd = get_count_by_creator(coll_hd, username)
    num_hw = get_count_by_creator(coll_hw, username)
    num_se = get_count_by_creator(coll_se, username)
    num_st = get_count_by_creator(coll_st, username)
    num_td = get_count_by_creator(coll_td, username)
    num_tm = get_count_by_creator(coll_tm, username)
    num_tsd = get_count_by_creator(coll_tsd, username)

    return num_ed + num_em + num_fd + num_hd + num_hw + num_se + num_st + num_td + num_tm + num_tsd


def update_group_data(doc_id, doc):
    print("It has not been made yet.")


def update_usage_info(doc_id, collection, user_name, num_dataset, num_hazard_dataset, num_hazard, num_dfr3, file_size, hazard_file_size):
    usage_json = {"className" : "edu.illinois.ncsa.incore.common.models.SpaceUsage",
                  "datasets": num_dataset, "hazardDatasets": num_hazard_dataset, "hazards": num_hazard,
                  "dfr3": num_dfr3, "datasetSize": file_size, "hazardDatasetSize": hazard_file_size}

    collection.update(
        {"_id": doc_id},
        {"$set": {"usage": usage_json}}
    )
    print("Update usage for ", user_name)


def query_dfr3_count(username, coll_f, coll_m, coll_r):
    num_f = get_count_by_creator(coll_f, username)
    num_m = get_count_by_creator(coll_m, username)
    num_r = get_count_by_creator(coll_r, username)

    return num_f + num_m + num_r


def query_datadb_status(collection, username, key_db):
    datasets = []

    if key_db.lower() == "hazard":
        datasets = get_dataset_by_creator(collection, username, True)
    elif key_db.lower() == "dataset":
        datasets = get_dataset_by_creator(collection, username, False)

    if len(datasets) == 0 or datasets is None:
        print("Could not find any datasets for ", username)

    total_num_dataset = len(datasets)
    total_file_size = 0

    # add the file size of all files in fileDescriptors
    for dataset in datasets:
        if 'fileDescriptors' in dataset:
            fds = dataset["fileDescriptors"]
            for fd in fds:
                total_file_size += int(fd["size"])

    return total_num_dataset, total_file_size


def get_dataset_by_creator(collection, creator, with_hazard):
    query = dict()
    if with_hazard:
        query_parts = [{'creator': creator}, {'dataType': {'$in': DATA_TYPE_HAZARD}}]
        query['$and'] = query_parts
    else:
        query_parts = [{'creator': creator}, {'dataType': {'$nin': DATA_TYPE_HAZARD}}]
        query['$and'] = query_parts

    db_data = collection.find(query)
    data_list = list(db_data)

    return data_list


def get_count_by_creator(collection, creator):
    count = collection.find({'creator': creator}).count()

    return count


if __name__ == '__main__':
    update_space_base_allocation_information()