# Retrofit Strategy and Cost Script 

## Description

A script to generate a retrofit strategy with given rules and to compute retrofit cost

## Files

- **base-data folder**: it contains the raw data to create duckdb file (rs_data.db)
- **rs_builder.py**: main script to genearte a retrofit strategy with given rules and to compute retrofit cost
- **retrofit_cost_galveston.py**: script to compute retrofit cost for Galveston
- **retrofit_cost_slc.py**: script to compute retrofit cost for SLC
- **retrofit_cost_joplin.py**: script to compute retrofit cost for Joplin
- **rs_data.db**: a duckdb file contains data needed for the script (detail description below)

- **rs_data_builder.py**: a script to create rs_data.db file


## Usage

Need to install "duckdb" (assumeing that it has **pyincore** installed)
```console
conda install python-duckdb -c conda-forge
```

run main script
```console
See test.sh 
```

## Input
```console
usage: rs_builder.py [-h] [--rules RULES] [--retrofits RETROFITS] [--result_name RESULT_NAME] [--token TOKEN]
                     [--service_url SERVICE_URL] [--spaces SPACES]

Generating Retrofit Strategy Dataset and Computing Retrofit Cost

options:
  -h, --help            show this help message and exit
  --rules RULES         Retrofit strategy rules
  --retrofits RETROFITS
                        Retrofit methods and values
  --result_name RESULT_NAME
                        Strategy Related Results Name
  --token TOKEN         Service token
  --service_url SERVICE_URL
                        Service endpoint
  --spaces SPACES       Spaces to write to (comma separated)
```

**Example for Galveston**
```json
    rules = {
        "testbed":"galveston",
        "rules": 3,
        "zones": ["1P", "1P", "0.2P"],
        "strtypes": ["1", "2", "1"],
        "pcts": [1,1,1]
    }
    retrofits = {
        "ret_keys":["elevation","elevation","elevation"],
        "ret_vals":[5, 10, 5]        
    }
```

**Example for SLC**
```json
    rules = {
        "testbed":"slc",
        "rules": 3,
        "zones": ["COUNCIL DISTRICT 1","COUNCIL DISTRICT 2","COUNCIL DISTRICT 3"],
        "strtypes": ["URML","URMM","URML"],
        "pcts": [10,20,20]
    }
    retrofits = {
        "ret_keys":["Wood or Metal Deck Diaphragms Retrofitted","Wood or Metal Deck Diaphragms Retrofitted","Wood or Metal Deck Diaphragms Retrofitted"],
        "ret_vals":["","",""]        
    }
```

## Output
### retrofit strategy file in CSV:
- columns: guid, retrofit_key, retrofit_value
### retrofit strategy file in Shapefile:
- columns: (geometry), guid, retrofit_k, retorfit_v, retrofit_c
### retrofit cost file in JSON
```json
    {
        "total": {
            "num_bldg": 3283,
            "num_bldg_no_cost": 42,
            "cost": 117260721.43
        },
        "by_rule": {
            "0": {
                "num_bldg": 3191,
                "num_bldg_no_cost": 40,
                "cost": 94393478.73
            },
            "1": {
                "num_bldg": 90,
                "num_bldg_no_cost": 0,
                "cost": 22867242.7
            },
            "2": {
                "num_bldg": 2,
                "num_bldg_no_cost": 2,
                "cost": 0
            }
        }
    }
```


## rs_data.db

### Preparing the shapefiles
Instead of doing spatial operation on-the-fly (e.g. find buildings in a zone by "intersect" or "contain"), preparing the data in QGIS
#### Modify the building inventory (in QGIS)
- Delete no-data columns 
- Delete buidings with structure types that are not used in retrofit 
- Spatial join the buliding inventory with zone (boundary) file to generate a column containing zone (boundary) id

### Loading the data to rs_data.db
- Please see the script (rs_data_builder.py) for actual SQL statement
- Note 1: use **spatial extension** of duckdb in order to export geometry to WKT -> it enables to create data in various format; and if we decide to do any spatial operation, we can use this db file.

### Tables in rs_data.db
- **slc**: SLC building inventory with zone (boundary)
- **galveston**: Galveston building inventory with zone (boundary)
- **joplin**: Joplin building inventory
- **slc_bldg_ret_cost**: SLC retrofit cost table (actual cost per building)
- **galveston_bldg_ret_cost**: Galveston retrofit cost table (lookup table with unit cost)
- **joplin_bldg_ret_cost**: Joplin retrofit unit cost table (lookup table with unit cost)

