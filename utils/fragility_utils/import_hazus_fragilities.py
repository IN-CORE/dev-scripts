import json
import csv
import xmltodict


def use_xml(xml_path, csv_path):
    with open(xml_path, 'rt', encoding='UTF16') as mvz_xml:
        root = xmltodict.parse(mvz_xml.read())

    root_obj= root['fragility-dataset']
    dataset_obj = root_obj['fragility-dataset-sets']
    frag_obj = dataset_obj['fragility-set']

    headers= [
                'ID', 'Fragility ID Code', 'Author', 'Structure Type',
                'Stories', 'Description', 'Ground Motions', 'Code',
                'Damage Type', 'Demand Type', 'Demand Units', 'Limit States',
                'T Eqn Type', 'T Eqn Param0', 'T Eqn Param1', 'T Eqn Param2',
                'Frag Eqn Type', 'Parameters',
                'Median0', 'Beta0',
                'Median1', 'Beta1',
                'Median2', 'Beta2',
                'FS Param0', 'FS Param1', 'FS Param2', 'FS Param3',
                'FS Param4', 'FS Param5', 'FS Param6', 'FS Param7',
                'FS Param8', 'FS Param9', 'FS Param10', 'FS Param11',
                'FS Param12', 'FS Param13', 'FS Param14', 'FS Param15',
                'FS Param16', 'FS Param17'
    ]

    # open csv file
    output = csv.writer(open(csv_path,'w', newline='\n'))
    output.writerow(['ID','Fragility ID Code','Author','Structure Type',
                'Stories','Description','Ground Motions','Code',
                'Damage Type','Demand Type','Demand Units','Limit States',
                'T Eqn Type','T Eqn Param0','T Eqn Param1','T Eqn Param2',
                'Frag Eqn Type','Parameters',
                'Median0','Beta0',
                'Median1','Beta1',
                'Median2','Beta2',
                'FS Param0','FS Param1','FS Param2','FS Param3',
                'FS Param4','FS Param5','FS Param6','FS Param7',
                'FS Param8','FS Param9','FS Param10','FS Param11',
                'FS Param12','FS Param13','FS Param14','FS Param15',
                'FS Param16','FS Param17'])

    i = 1562    # the first id number to insert to existing excel file.
    for frag in frag_obj:
        prop_obj = frag['fragility-set-properties']

        # if prop_obj['@Author'].lower() = "hazus" and prop_obj["@"]
        if prop_obj['@Author'].lower() == "hazus":
            frag_set_obj = frag['fragility-set-fragilities']
            curve_obj = frag_set_obj['fragility-curve']
            output.writerow([
                i, prop_obj['@ID'], prop_obj['@Author'], prop_obj['@StructureType'],
                prop_obj['@Stories'], prop_obj['@Description'],prop_obj['@GroundMotions'], prop_obj['@Code'],
                prop_obj['@DamageType'], prop_obj['@DemandType'],prop_obj['@DemandUnits'], prop_obj['@LimitStates'],
                prop_obj['@TEqnType'], prop_obj['@TEqnParam0'], prop_obj['@TEqnParam1'], prop_obj['@TEqnParam2'],
                prop_obj['@FragEqnType'], prop_obj['@Parameters'],
                curve_obj[0]['@fragility-curve-median'], curve_obj[0]['@fragility-curve-beta'],
                curve_obj[1]['@fragility-curve-median'], curve_obj[1]['@fragility-curve-beta'],
                curve_obj[2]['@fragility-curve-median'], curve_obj[2]['@fragility-curve-beta'],
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0
            ])
            i += 1


def use_json(json_path, csv_path):
    x = open(json_path)
    x = json.load(x)

    f = csv.writer(open(csv_path,'w', newline='\n'))

    # Write CSV Header
    f.writerow(['ID','Fragility ID Code','Author','Structure Type','Stories','Description',
                'Ground Motions','Code','Damage Type','Demand Type','Demand Units','Limit States',
                'T Eqn Type','T Eqn Param0','T Eqn Param1','T Eqn Param2','Frag Eqn Type','Parameters',
                'Median0','Beta0',
                'Median1','Beta1',
                'Median2','Beta2',
                'FS Param0','FS Param1','FS Param2','FS Param3','FS Param4','FS Param5','FS Param6',
                'FS Param7','FS Param8','FS Param9','FS Param10','FS Param11','FS Param12','FS Param13',
                'FS Param14','FS Param15','FS Param16','FS Param17'])

    i = 1
    for x in x:
        f.writerow([i, x["legacyId"], x["authors"][0], x["inventoryType"], 'N/A', x["description"],
                    'N/A', 'N/A', 'N/A', x["demandType"], x["demandUnits"], 'N/A',
                    '1', '0', '0', '0', 'N/A', 'N/A',
                    x["fragilityCurves"][0]["median"], x["fragilityCurves"][0]["beta"],
                    x["fragilityCurves"][1]["median"], x["fragilityCurves"][1]["beta"],
                    x["fragilityCurves"][2]["median"], x["fragilityCurves"][2]["beta"],
                    '0', '0', '0', '0', '0', '0', '0'
                    '0', '0', '0', '0', '0', '0', '0'
                    '0', '0', '0', '0'
                   ]
                   )
        i += 1

if __name__ == "__main__":
    xml_path = 'data\\FRAG_Centerville_Building_Fragilities.xml'
    json_path = 'data\\missing_hazus_earthquake_fragilities.json'
    csv_path = 'data\\test.csv'
    use_xml(xml_path, csv_path)