# Retrofit Strategy and Cost Script 

## Description

A script to generate a retrofit strategy with given rules and to compute retrofit cost

## Files

- **base-data folder**: it contains the raw data to create duckdb file (rs_data.db)
- **rs_builder.py**: main script to genearte a retrofit strategy with given rules and to compute retrofit cost
- **retrofit_cost_galveston.py**: script to compute retrofit cost for Galveston
- **retrofit_cost_slc.py**: script to compute retrofit cost for SLC
- **rs_data.db**: a duckdb file contains data needed for the script (detail description below)

- **rs_data_builder.py**: a script to create rs_data.db file


## Usage

Need to install "duckdb" (assumeing that it has **pyincore** installed)
```console
conda install python-duckdb -c conda-forge
```

run main script
'''console
python rs_builder.py
'''

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
- **slc_bldg_ret_cost**: SLC retrofit cost table (actual cost per building)
- **galveston_bldg_ret_cost**: Galveston retrofit cost table (lookup table with unit cost)

