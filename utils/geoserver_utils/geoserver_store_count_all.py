import requests
import json

# GeoServer REST API URL and credentials
GEOSERVER_URL = "https://incore.ncsa.illinois.edu/geoserver/rest"
USERNAME = "admin"
PASSWORD = "4etsAudpNvq8KXX3"


# Function to get list of all data stores in a workspace
def get_data_stores(workspace):
    url = f"{GEOSERVER_URL}/workspaces/{workspace}/datastores.json"
    response = requests.get(url, auth=(USERNAME, PASSWORD))

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return []

    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            data = response.json()
        except json.JSONDecodeError as err:
            print(f"JSON decode error occurred: {err}")
            print(f"Response content: {response.content.decode('utf-8')}")
            return []
        return data.get("dataStores", {}).get("dataStore", [])
    else:
        print(f"Unexpected content type: {content_type}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return []


# Main function to list all active data stores
def list_active_data_stores():
    workspaces_url = f"{GEOSERVER_URL}/workspaces.json"
    response = requests.get(workspaces_url, auth=(USERNAME, PASSWORD))

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return

    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            workspaces = response.json().get("workspaces", {}).get("workspace", [])
        except json.JSONDecodeError as err:
            print(f"JSON decode error occurred: {err}")
            print(f"Response content: {response.content.decode('utf-8')}")
            return
    else:
        print(f"Unexpected content type: {content_type}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return

    # count total number of data stores
    count = 0

    for workspace in workspaces:
        ws_name = workspace["name"]
        data_stores = get_data_stores(ws_name)
        for data_store in data_stores:
            ds_name = data_store["name"]
            count += 1
            print(f"Active data store: {ws_name}:{ds_name}")

    print(f"Total number of data stores: {count}")

if __name__ == "__main__":
    list_active_data_stores()
