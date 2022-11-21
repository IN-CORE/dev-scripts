#!/usr/bin/env python

from pymongo import MongoClient
# client = MongoClient('incore2-mongo1.ncsa.illinois.edu', 27017)
# client = MongoClient('incore2-mongo-dev.ncsa.illinois.edu', 27017)
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://root:passwordhere@localhost:28017/')
db = client['dfr3db']

for doc in db["FragilitySet"].find():
    print(doc)
    curves = doc['fragilityCurves']
    refactoredCurves = []
    for curve in curves:
        curve['className'] = 'edu.illinois.ncsa.incore.service.dfr3.models.DFR3Curve'
        if 'fragilityCurveParameters' in curve:
            curve['curveParameters'] = curve['fragilityCurveParameters']
            del curve['fragilityCurveParameters']
        refactoredCurves.append(curve)

    doc['fragilityCurves'] = refactoredCurves
    doc['curveParameters'] = doc['fragilityCurveParameters']
    del doc['fragilityCurveParameters']

    refactoredCurveParameters = []
    for cp in doc['curveParameters']:
        cp['className'] = 'edu.illinois.ncsa.incore.service.dfr3.models.CurveParameter'
        refactoredCurveParameters.append(cp)
    doc['curveParameters'] = refactoredCurveParameters
    print(doc)
    # db["FragilitySet"].replace_one({'_id': doc['_id']}, doc)








