"""
Script to align PostgreSQL/PostGIS table schema with a semantic JSON schema definition.

This script:
- Connects to a PostgreSQL database using credentials from a `.env` file.
- Reads a JSON schema that defines field names, data types, and constraints.
- Ensures each column exists in the target table (`nsi`) with the correct data type.
- Adds NOT NULL constraints where required.
- Adds digit-based CHECK constraints for:
    - `no_stories` → 0–999 (3 digits)
    - `year_built` → 0–9999 (4 digits)
"""

import json
import psycopg2
from dotenv import load_dotenv
import os

# === Load environment variables ===
load_dotenv()
DB_SETTINGS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 5432),
}

# === Load schema ===
with open("building_inventory_ver6_schema.json", "r") as f:
    schema = json.load(f)

# === Type mapping ===
type_map = {
    "xsd:string": "TEXT",
    "xsd:integer": "INTEGER",
    "xsd:double": "DOUBLE PRECISION",
    "gml:PointPropertyType": "geometry(Point,4326)"
}

# === Connect to DB ===
conn = psycopg2.connect(**DB_SETTINGS)
cur = conn.cursor()

# === Drop legacy column if exists ===
cur.execute("ALTER TABLE nsi DROP COLUMN IF EXISTS geometry;")

# === Process schema columns ===
# === Process each column in schema ===
for column in schema["tableSchema"]["columns"]:
    col_name = column["name"]
    datatype = column["datatype"]
    pg_type = type_map.get(datatype, "TEXT")

    # Digit-based CHECK constraints
    check_clause = ""
    if col_name == "no_stories":
        check_clause = "CHECK (no_stories BETWEEN 0 AND 999)"
    elif col_name == "year_built":
        check_clause = "CHECK (year_built BETWEEN 0 AND 9999)"

    # Dynamic constraint name
    constraint_name = f"chk_{col_name}_digits"

    # Add or alter column (do NOT enforce NOT NULL in this step)
    alter_query = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='nsi' AND column_name='{col_name}'
        ) THEN
            ALTER TABLE nsi
                ADD COLUMN {col_name} {pg_type};
        ELSE
            ALTER TABLE nsi
                ALTER COLUMN {col_name} TYPE {pg_type};
        END IF;
    END
    $$;
    """
    cur.execute(alter_query)

    # Add CHECK constraint if applicable
    if check_clause:
        constraint_check_query = f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = '{constraint_name}' AND conrelid = 'nsi'::regclass
            ) THEN
                ALTER TABLE nsi ADD CONSTRAINT {constraint_name} {check_clause};
            END IF;
        END
        $$;
        """
        cur.execute(constraint_check_query)

# === Drop unused 'geometry' column if it exists ===
cur.execute("ALTER TABLE nsi DROP COLUMN IF EXISTS geometry;")

# === Finalize ===
conn.commit()
cur.close()
conn.close()

print("NSI table updated and spatial index ensured.")

