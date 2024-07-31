import requests
from requests.auth import HTTPBasicAuth

# GeoServer configuration
GEOSERVER_URL = "https://incore.ncsa.illinois.edu/geoserver"
GEOSERVER_USERNAME = "admin"
GEOSERVER_PASSWORD = "4etsAudpNvq8KXX3"

def get_workspaces():
    url = f"{GEOSERVER_URL}/rest/workspaces"
    response = requests.get(url, auth=HTTPBasicAuth(GEOSERVER_USERNAME, GEOSERVER_PASSWORD))
    response.raise_for_status()
    return response.json()["workspaces"]["workspace"]

def get_data_stores(workspace_name):
    url = f"{GEOSERVER_URL}/rest/workspaces/{workspace_name}/datastores"
    response = requests.get(url, auth=HTTPBasicAuth(GEOSERVER_USERNAME, GEOSERVER_PASSWORD))
    response.raise_for_status()
    return response.json()["dataStores"]["dataStore"]

def get_data_store_details(workspace_name, data_store_name):
    url = f"{GEOSERVER_URL}/rest/workspaces/{workspace_name}/datastores/{data_store_name}"
    response = requests.get(url, auth=HTTPBasicAuth(GEOSERVER_USERNAME, GEOSERVER_PASSWORD))
    response.raise_for_status()
    return response.json()

def delete_data_store(workspace_name, data_store_name):
    url = f"{GEOSERVER_URL}/rest/workspaces/{workspace_name}/datastores/{data_store_name}?recurse=true"
    response = requests.delete(url, auth=HTTPBasicAuth(GEOSERVER_USERNAME, GEOSERVER_PASSWORD))
    response.raise_for_status()
    print(f"Deleted data store: {data_store_name} in workspace: {workspace_name}")

def check_and_remove_jdbc_data_stores():
    workspaces = get_workspaces()
    for workspace in workspaces:
        workspace_name = workspace["name"]
        print(f"Checking workspace: {workspace_name}")
        data_stores = get_data_stores(workspace_name)
        for data_store in data_stores:
            data_store_name = data_store["name"]
            details = get_data_store_details(workspace_name, data_store_name)
            if "connectionParameters" in details["dataStore"] and "dbtype" in details["dataStore"]["connectionParameters"]:
                dbtype = details["dataStore"]["connectionParameters"]["dbtype"]
                if dbtype == "postgis" or dbtype == "oracle" or dbtype == "mysql" or dbtype == "db2":
                    print(f"Data store {data_store_name} in workspace {workspace_name} uses JDBC (dbtype: {dbtype}). Deleting...")
                    # delete_data_store(workspace_name, data_store_name)
                else:
                    print(f"Data store {data_store_name} in workspace {workspace_name} does not use JDBC (dbtype: {dbtype}).")
            else:
                # print(f"Data store {data_store_name} in workspace {workspace_name} does not have connection parameters.")
                pass

if __name__ == "__main__":
    check_and_remove_jdbc_data_stores()
