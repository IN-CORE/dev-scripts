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


# Function to activate a data store
def activate_data_store(workspace, datastore):
    url = f"{GEOSERVER_URL}/workspaces/{workspace}/datastores/{datastore}.json"
    headers = {"Content-type": "application/json"}
    data = {"dataStore": {"enabled": True}}
    response = requests.put(url, auth=(USERNAME, PASSWORD), headers=headers, data=json.dumps(data))
    try:
        response.raise_for_status()
        print(f"Activated data store: {datastore} in workspace: {workspace}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while activating data store {datastore} in workspace {workspace}: {err}")
        print(f"Response content: {response.content.decode('utf-8')}")


# Main function to activate all data stores
def activate_all_data_stores():
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
            print(f"Activating data store: {ws_name}:{ds_name}")
            activate_data_store(ws_name, ds_name)


if __name__ == "__main__":
    activate_all_data_stores()
