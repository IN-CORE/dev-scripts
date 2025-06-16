import requests
import json

# GeoServer REST API URL and credentials
GEOSERVER_URL = "https://incore-tst.ncsa.illinois.edu/geoserver/rest"
USERNAME = "admin"
PASSWORD = "IncoreGEO2024!"


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


# Function to check if a data store is problematic
def is_problematic_data_store(workspace, datastore):
    url = f"{GEOSERVER_URL}/workspaces/{workspace}/datastores/{datastore}.json"
    response = requests.get(url, auth=(USERNAME, PASSWORD))

    try:
        response.raise_for_status()
        return False  # If we can get the metadata successfully, it's not problematic
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while checking data store {datastore} in workspace {workspace}: {err}")
        print(f"Response content: {response.content.decode('utf-8')}")
        return True  # If there's an HTTP error, consider it problematic


# Function to dispose of a problematic data store
def dispose_data_store(workspace, datastore):
    url = f"{GEOSERVER_URL}/workspaces/{workspace}/datastores/{datastore}.json"
    response = requests.delete(url, auth=(USERNAME, PASSWORD))
    try:
        response.raise_for_status()
        print(f"Disposed data store: {datastore} in workspace: {workspace}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while disposing data store {datastore} in workspace {workspace}: {err}")
        print(f"Response content: {response.content.decode('utf-8')}")


# Main function to check and dispose problematic data stores
def check_and_dispose_problematic_data_stores():
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

    for workspace in workspaces:
        ws_name = workspace["name"]
        data_stores = get_data_stores(ws_name)
        for data_store in data_stores:
            ds_name = data_store["name"]
            print(f"Checking data store: {ws_name}:{ds_name}")
            if is_problematic_data_store(ws_name, ds_name):
                print(f"Disposing problematic data store: {ws_name}:{ds_name}")
                dispose_data_store(ws_name, ds_name)


if __name__ == "__main__":
    check_and_dispose_problematic_data_stores()
