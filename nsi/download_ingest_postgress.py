import requests
import geopandas as gpd
import os
import subprocess
import time
from sqlalchemy import create_engine

# Define NSI API endpoint
BASE_URL = "https://nsi.sec.usace.army.mil/nsiapi/structures?fips="

# Define state FIPS codes
STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "FL": "12", "GA": "13", "HI": "15", "ID": "16",
    "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21", "LA": "22",
    "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
    "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
    "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39", "OK": "40",
    "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46", "TN": "47",
    "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53", "WV": "54",
    "WI": "55", "WY": "56"
}

# PostgreSQL/PostGIS connection details for local port-forwarding
PG_HOST = "localhost"
PG_PORT = "54321"  # Forwarded port
PG_DATABASE = "nsi_db"
PG_USER = "postgres"
PG_PASSWORD = "your_password"

# Create database connection string
DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# Directory to store downloaded files
SAVE_DIR = "nsi_data"
os.makedirs(SAVE_DIR, exist_ok=True)

# Start port-forwarding as a subprocess
print("Starting Kubernetes port-forward...")
port_forward_cmd = [
    "kubectl", "port-forward", "-n", "incore",
    "services/incore-postgresql", f"{PG_PORT}:5432"
]
port_forward_process = subprocess.Popen(port_forward_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Give port-forward time to establish connection
time.sleep(5)

# Create PostGIS connection
engine = create_engine(DATABASE_URL)

try:
    # Download and insert each state's data
    for state, fips_code in STATE_FIPS.items():
        url = f"{BASE_URL}{fips_code}"
        file_path = os.path.join(SAVE_DIR, f"{state}.geojson")

        print(f"Downloading {state} data from {url}...")

        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Saved {state} data to {file_path}")

            # Load into GeoPandas
            gdf = gpd.read_file(file_path)

            # Convert to EPSG:4326 (WGS84) for PostGIS compatibility
            if gdf.crs is None or gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            # Push to PostGIS
            table_name = f"nsi_{state.lower()}"
            print(f"Inserting {state} data into PostGIS table '{table_name}'...")
            gdf.to_postgis(table_name, engine, if_exists="replace", index=False)
            print(f"Inserted {state} data into '{table_name}' successfully.")

        else:
            print(f"Failed to download {state} data. Status Code: {response.status_code}")

finally:
    # Stop port-forwarding when done
    print("Stopping port-forward...")
    port_forward_process.terminate()

print("Download and PostGIS import completed for all states.")
