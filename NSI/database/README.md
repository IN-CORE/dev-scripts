# NSI Data Processing Utilities

This repository contains a set of Bash and Python scripts for processing, converting, and ingesting NSI (National Structure Inventory) data into a PostgreSQL/PostGIS database. These tools support workflows involving GeoJSON, GeoPackage (GPKG), and zipped input formats.

---

## Overview

These scripts are designed to:
- Convert NSI GeoJSON or GeoPackage files into PostgreSQL-compatible formats.
- Split large files into manageable chunks.
- Automate ingestion into a Kubernetes-hosted PostGIS database.
- Zip/unzip data during conversion workflows.
- Clean up temporary or intermediate files.
- Assign regional metadata during batch conversion.

---

## Requirements

- Bash
- Python 3
- GDAL (with `ogr2ogr` and `ogrinfo`)
- `kubectl` CLI
- PostgreSQL/PostGIS running in Kubernetes
- Python packages: `geopandas`, `pyincore-data`

---

## Scripts

### ingest_geojson_to_postgis.sh

Imports a single GeoJSON file into a PostgreSQL/PostGIS table via Kubernetes port-forwarding.

**Usage:**
```
./ingest_geojson_to_postgis.sh <geojson-file> [overwrite|append]
```

---

### run_ingest.sh

Batch-ingests all GeoJSON chunks in the `chunks/` directory using the ingestion script above.

**Usage:**
```
./run_ingest.sh
```

---

### split_and_ingest.sh

Splits a large GeoJSON file into 10,000-feature chunks and imports them into the `nsi` PostGIS table.

**Usage:**
```
./split_and_ingest.sh <geojson-file> <layer-name>
```

---

### split_geojson.py

Splits a large GeoJSON file into smaller chunks using Python and GeoPandas.

**Usage:**
```
python split_geojson.py <input.geojson> <features-per-file>
```

---

### geojson_to_sql_append.sh

Converts a GeoJSON file into a SQL dump that can be safely appended to the `nsi` table.

**Usage:**
```
./geojson_to_sql_append.sh <input.geojson>
```

---

### ingest_zipped_gpkg.sh

Unzips a `.zip` containing a `.gpkg`, converts it to SQL, and executes it inside a PostgreSQL pod.

**Usage:**
```
./ingest_zipped_gpkg.sh <input_file.zip>
```

---

### convert_nsi_zip_to_inventory_gpkg.py

Converts NSI `.zip` files containing GeoJSONs into region-tagged GPKG files using `pyincore_data`, zips them, and stores them in an output directory.

**Usage:**
```
python convert_nsi_zip_to_inventory_gpkg.py \
    --input-dir ./zips \
    --csv ./state_groups.csv \
    --output-dir ./gpkg_output
```

---

### zip_by_state.sh

Zips all `.geojson` files in the current directory into separate `.zip` files based on state abbreviations.

**Usage:**
```
./zip_by_state.sh
```

---

### sync_pg_table_with_schema.py

Synchronizes the `nsi` table in a PostgreSQL/PostGIS database with a semantic schema defined in a JSON file.

**Features:**
- Adds missing columns based on the schema definition.
- Alters column types to match those in the schema if needed.
- Applies `NOT NULL` constraints where specified.
- Adds digit-based `CHECK` constraints:
  - `no_stories` must be a 3-digit integer (0–999)
  - `year_built` must be a 4-digit integer (0–9999)
- Uses a `.env` file for PostgreSQL connection configuration.

**Usage:**

```
python sync_pg_table_with_schema.py
```

**.env file format:**

```
DB_NAME=your_db_name
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
```

Ensure the `schema_definition.json` file is present in the same directory before running the script.
---

## Common Workflows

### Ingest zipped NSI GeoPackage into a Kubernetes-hosted PostGIS database

Use the following command:

```
./ingest_zipped_gpkg.sh <input_file.zip>
```

This will:
- Unzip the `.gpkg` file,
- Convert it to a SQL dump (safe for appending),
- Copy it into the running PostgreSQL pod,
- Execute the SQL file to ingest data into the `nsi` table,
- Clean up temporary files.

---

### Convert zipped NSI GeoJSON into IN-CORE Building Inventory GPKG format

Use the following command:

```
python convert_nsi_zip_to_inventory_gpkg.py \
    --input-dir ./zips \
    --csv ./state_groups.csv \
    --output-dir ./gpkg_output
```

This will:
- Load all ZIP files from the input directory,
- Extract and convert GeoJSONs using regional mapping from the CSV,
- Write `.gpkg` files per state and compress them into ZIP files in `output_gpkg/`,
- Remove intermediate files automatically.

---

### Split a large GeoJSON into smaller chunks and ingest into PostGIS

Use the following command:

```
./split_and_ingest.sh <geojson-file> <layer-name>
```

This will:
- Split the input GeoJSON into chunks of 10,000 features,
- Store the chunks in a `chunks/` directory,
- Start a Kubernetes port-forward to the PostGIS service,
- Import the first chunk using `overwrite` mode and the rest with `append`.

---

### Convert a GeoJSON file into a SQL script (safe to append) for PostGIS

Use the following command:

```
./geojson_to_sql_append.sh <input.geojson>
```

This will:
- Convert the GeoJSON to a PostgreSQL-compatible SQL file (`nsi.sql`),
- Strip out `DROP TABLE` and `CREATE TABLE` statements to make it append-safe.

---

### Batch ingest multiple GeoJSON chunks into PostGIS

Use the following command:

```
./run_ingest.sh
```

This will:
- Loop over files matching `chunks/chunk_*.geojson`,
- Use `ingest_geojson_to_postgis.sh` to append each one into the database.

---

### Split a large GeoJSON using Python for offline chunking

Use the following command:

```
python split_geojson.py <input.geojson> <features-per-file>
```

This will:
- Use GeoPandas to load the full GeoJSON,
- Split it into evenly sized chunks,
- Write each chunk as `chunk_000.geojson`, `chunk_001.geojson`, etc.

---

### Zip all `.geojson` files by state abbreviation

Use the following command:

```
./zip_by_state.sh
```

This will:
- Loop through all `.geojson` files in the current directory,
- Create a `.zip` archive for each using the same base name.

### Ingest zipped NSI GeoPackage into a Kubernetes-hosted PostGIS database

Use the following command:

```
./ingest_zipped_gpkg.sh <input_file.zip>
```

This will:
- Unzip the `.gpkg` file,
- Convert it to a SQL dump (safe for appending),
- Copy it into the running PostgreSQL pod,
- Execute the SQL file to ingest data into the `nsi` table,
- Clean up temporary files.

---

### Convert zipped NSI GeoJSON into IN-CORE Building Inventory GPKG format

Use the following command:

```
python convert_nsi_zip_to_inventory_gpkg.py \
    --input-dir ./zips \
    --csv ./state_groups.csv \
    --output-dir ./gpkg_output
```

This will:
- Load all ZIP files from the input directory,
- Extract and convert GeoJSONs using regional mapping from the CSV,
- Write `.gpkg` files per state and compress them into ZIP files in `output_gpkg/`,
- Remove intermediate files automatically.

---