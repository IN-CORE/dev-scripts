"""
This is a script for updating the owner of any service object to be owned by incore if the object is in the public
incore space
"""
from pymongo import MongoClient

auth_needed = False
mongo_username = ""
mongo_password = ""

host = "localhost"  #local
# host = "incore2-mongo1" # prod
# host = "incore2-mongo-dev"  # dev
port = "27017"

if auth_needed:
    client = MongoClient('mongodb://%s:%s@%s:%s' % (mongo_username, mongo_password, host, port))
else:
    client = MongoClient('mongodb://%s:%s' % (host, port))



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

db = client['spacedb']

members = None
for doc in db["Space"].find():
    # print(type(doc))
    # print(type(doc['metadata']))
    if doc['metadata']['name'] == 'incore':
        members = doc['members']
        break

# print(members)
    
for collection in collections:
    for document in collection["collection"].find():
        if str(document['_id']) in members :
            # found incore space object, check the owner
            if document['owner'] != 'incore':
                # object is in the incore space, but incore is not the owner, this should be updated
                document['owner'] = 'incore'
                collection["collection"].replace_one({'_id':document['_id']}, document)
