#!/usr/bin/env python

from pymongo import MongoClient
# client = MongoClient('incore2-mongo1.ncsa.illinois.edu', 27017)
# client = MongoClient('incore2-mongo-dev.ncsa.illinois.edu', 27017)
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://root:passwordhere@localhost:28017/')
db = client['datadb']

for doc in db["Dataset"].find():
    if 'spaces' in doc:
        print(doc)
        del doc['spaces']
        db["Dataset"].replace_one({'_id': doc['_id']}, doc)








