# NSI Conversion and Query Utilities

This repository contains Python scripts for converting National Structure Inventory (NSI) datasets to IN-CORE-compatible building inventory formats and querying them from a PostgreSQL/PostGIS database.

---

## Overview

These tools help with:
- Converting raw NSI GeoPackages to IN-CORE building inventory format
- Enriching NSI data with region, FIPS, and GUID fields
- Uploading GeoDataFrames to a PostGIS database
- Downloading NSI data by FIPS or state
- Querying the `nsi_raw` table from PostGIS using FIPS or bounding box

---

## Requirements

- Python 3.x
- PostgreSQL with PostGIS enabled
- Python packages:
  - pandas
  - geopandas
  - fiona
  - sqlalchemy
  - requests
  - geojson
- A `config.py` file providing a `Config` class with:
  - DB connection info
  - NSI data URLs
  - Prefixes

---

## Scripts

### convert_nsi_to_building_inventory.py

Batch converts multiple state NSI GeoPackages into IN-CORE-compatible building inventories using a CSV-based state-to-region mapping. Saves `.gpkg` output to disk.

**Usage:**
```
python convert_nsi_to_building_inventory.py
```

---

### nsibuildinginventory.py

Fetches NSI data by county FIPS codes and uploads them to a PostGIS database. Also includes an optional (commented) method to save data as `.gpkg`.

**Usage:**
```
python nsibuildinginventory.py
```

---

### nsiutil.py

Utility module containing functions for:
- Downloading NSI GeoPackages by state or FIPS
- Adding FIPS and GUID columns
- Converting GeoPackages to GeoDataFrames
- Uploading GeoDataFrames to PostGIS
- Writing GeoPackages to disk

This module is imported and used by other scripts (not intended to be executed directly).

---

### query.py

Provides database query utilities for the `nsi_raw` PostGIS table, including:
- A connection test
- Querying by FIPS
- A (placeholder) bounding box query

**Usage:**
```
python query.py
```

---

## Common Workflows

### Convert NSI GeoPackages to IN-CORE Building Inventories

```
python convert_nsi_to_building_inventory.py
```

- Requires: input files in `nsi_data/missing/` and `StateToGroup_missing.csv`
- Output saved to: `nsi_data/`

---

### Fetch NSI data by FIPS and upload to PostGIS

```
python nsibuildinginventory.py
```

- Loads first two FIPS codes from `data/us_county_fips_2018.csv`
- Fetches NSI data via API and uploads to the `nsi_raw` table

---

### Query PostGIS for a single FIPS or bounding box

```
python query.py
```

- Modify `query_test_fips()` or `query_test_bbox()` to suit your needs
- Output written to the `data/` folder as `.gpkg`

---

## Author

[Your Name or Organization]
