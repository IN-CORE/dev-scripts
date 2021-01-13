#!/usr/bin/env python
# coding: utf-8

# In[19]:


from pymongo import MongoClient
# client = MongoClient('incore2-mongo1.ncsa.illinois.edu', 27017)
# client = MongoClient('incore2-mongo-dev.ncsa.illinois.edu', 27017)
client = MongoClient('localhost', 27017)
db = client['datadb']

for doc in db["Dataset"].find():
    if 'boundingBox' in doc and doc['boundingBox'] == None:
        print(doc["_id"], doc["dataType"])
        del doc['boundingBox']
        db["Dataset"].replace_one({'_id':doc['_id']}, doc)






