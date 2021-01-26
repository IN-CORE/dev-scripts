#!/usr/bin/env python
# coding: utf-8

# In[13]:


from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("localhost", 27017) # local
# client = MongoClient("incore2-mongo1.ncsa.illinois.edu", 27017) # prod
# client = MongoClient("incore2-mongo-dev.ncsa.illinois.edu", 27017) #dev


# In[14]:


collections = [
    {"collection":client['datadb']['Dataset'], 
     "className":"edu.illinois.ncsa.incore.service.data.models.Dataset"},
    {"collection":client['dfr3db']['FragilitySet'],
     "className":"edu.illinois.ncsa.incore.service.dfr3.models.FragilitySet"},
    {"collection":  client['dfr3']['MappingSet'],
     "className":"edu.illinois.ncsa.incore.service.dfr3.models.MappingSet"},
    {"collection": client['dfr3']['RepairSet'], 
     "className":"edu.illinois.ncsa.incore.service.dfr3.models.RepairSet"},
    {"collection": client['dfr3']['RestorationSet'], 
     "className":"edu.illinois.ncsa.incore.service.dfr3.models.RestorationSet"},
    {"collection": client['hazarddb']['EarthquakeDataset'], 
     "className":"edu.illinois.ncsa.incore.service.hazard.models.eq.EarthquakeDataset"},
    {"collection": client['hazarddb']['EarthquakeModel'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.eq.EarthquakeModel"},
    {"collection":  client['hazarddb']['FloodDataset'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.flood.FloodDataset"},
    {"collection": client['hazarddb']['HurricaneDataset'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.hurricane.HurricaneDataset"},
    {"collection": client['hazarddb']['HurricaneWindfields'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.hurricaneWindfields.HurricaneWindfields"},
    {"collection": client['hazarddb']['ScenarioEarthquake'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.eq.ScenarioEarthquake"},
    {"collection":  client['hazarddb']['ScenarioTornado'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.tornado.ScenarioTornado"},
    {"collection":client['hazarddb']['TornadoDataset'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.tornado.TornadoDataset"},
    {"collection":client['hazarddb']['TornadoModel'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.tornado.TornadoModel"},
    {"collection": client['hazarddb']['TsunamiDataset'],
     "className":"edu.illinois.ncsa.incore.service.hazard.models.tsunami.TsunamiDataset"}
]               


# In[15]:


for collection in collections:
    for document in collection["collection"].find():
        if "className" not in document:
            print(document['_id'], "missing className")
            document["className"] = collection["className"]
        elif document["className"] != collection["className"]:
            print(document['_id'], document["className"])
            document["className"] = collection["className"]
            
        collection["collection"].replace_one({'_id':document['_id']}, document)


# In[ ]:




