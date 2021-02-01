#!/usr/bin/env python
# coding: utf-8

# In[19]:


from pymongo import MongoClient
# client = MongoClient('incore2-mongo1.ncsa.illinois.edu', 27017)
# client = MongoClient('incore2-mongo-dev.ncsa.illinois.edu', 27017)
client = MongoClient('localhost', 27017)
db = client['dfr3db']

for doc in db["FragilitySet"].find():
    if 'demandType' in doc:
        doc['demandType'] = [doc['demandType']]
        doc['units'] = [doc['demandUnits']]
        del doc['demandUnits']
        db["FragilitySet"].replace_one({'_id': doc['_id']}, doc)
    else:
        print(doc)
        print("bad data - every doc should be having demand type")

# Hack so that demand types and units are next to each other in the mongo document.
db["FragilitySet"].update_many({}, {"$rename": {"demandType": "demandTypes", "units": "demandUnits"}})




