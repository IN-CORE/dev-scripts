#!/usr/bin/env python3

"""
import data from webdav (earthquake.ncsa.illinois.edu) and
store them to incore2 data repository
"""
import os, sys
import csv

from pymongo import MongoClient


def main():
    mongo_url = "localhost"
    db_name = ''
    coll_name = ''
    field_name = ""

    csv_filename = 'datatype_mapping.csv'
    csv_file = os.path.join(os.getcwd(), csv_filename)

    orig_list, new_list = read_csv_file(csv_file)

    update_mongo_document_by_mapping(mongo_url, db_name, coll_name, field_name, orig_list, new_list)


"""read csv file"""
def read_csv_file(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        main_list = list(reader)

    # separate the columns
    orig_list = []
    new_list = []

    for i in range(len(main_list)):
        orig_list.append(main_list[i][0])
        new_list.append(main_list[i][1])

    return  orig_list, new_list

"""update records using mapping file"""
def update_mongo_document_by_mapping(mongo_url, db_name, coll_name, field_name, orig_list, new_list):
    client = MongoClient(mongo_url, 27017)
    db = client[db_name]
    coll = db[coll_name]

    for i in range(len(orig_list)):
        orig_datatype = orig_list[i]
        new_datatype = new_list[i]
        # coll.updateMany({field_name: original_datatype}, {'$set': {field_name: new_datatype}})
        result = coll.update({field_name: orig_datatype}, {'$set': {field_name: new_datatype}}, multi=True)
        print(orig_datatype, new_datatype, result)

if __name__ == "__main__":
    main()