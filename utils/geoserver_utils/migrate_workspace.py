import requests
from pymongo import MongoClient
from requests.auth import HTTPBasicAuth

# Configuration for GeoServer and MongoDB
GEOSERVER_URL = "http://localhost:8081/geoserver/rest"
GEOSERVER_USER = "admin"
GEOSERVER_PASSWORD = "geoserver"
MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "datadb"
COLLECTION_NAME = "Dataset"


# Function to create a new workspace in GeoServer
def create_workspace(workspace_name):
    headers = {'Content-type': 'text/xml'}
    data = f"<workspace><name>{workspace_name}</name></workspace>"
    url = f"{GEOSERVER_URL}/workspaces"

    response = requests.post(url, auth=(GEOSERVER_USER, GEOSERVER_PASSWORD), headers=headers, data=data)
    if response.status_code == 201:
        print(f"Workspace '{workspace_name}' created successfully.")
    elif response.status_code == 409:
        print(f"Workspace '{workspace_name}' already exists.")
    else:
        print(f"Failed to create workspace '{workspace_name}': {response.content}")


# Function to move a layer to a new workspace
def move_layer_to_workspace(layer_name, source_workspace, target_workspace):
    headers = {'Content-type': 'text/xml'}
    url = f"{GEOSERVER_URL}/layers/{source_workspace}:{layer_name}"

    # Update the target workspace for the layer
    data = f"<layer><defaultStyle><name>{target_workspace}:{layer_name}</name></defaultStyle></layer>"
    response = requests.put(url, auth=(GEOSERVER_USER, GEOSERVER_PASSWORD), headers=headers, data=data)

    if response.status_code == 200:
        print(f"Layer '{layer_name}' moved to workspace '{target_workspace}'.")
    else:
        print(f"Failed to move layer '{layer_name}': {response.content}")


# def change_workspace(source_workspace, target_workspace, dataset_id):
#     # Get datastore information
#     datastore_info = get_datastore(source_workspace, dataset_id)
#
#     if datastore_info:
#         # Move the datastore to the new workspace
#         datastore_info['dataStore']['workspace'] = {'name': target_workspace}
#         update_datastore(target_workspace, dataset_id, datastore_info)
#
#         # Move the layer to the new workspace
#         update_layer(target_workspace, dataset_id)
#
#     else:
#         print("Datastore not found or error occurred.")


def get_datastore(workspace, datastore):
    url = f'{GEOSERVER_URL}/workspaces/{workspace}/datastores/{datastore}.json'
    response = requests.get(url, auth=HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get datastore. Status code: {response.status_code}")
        return None


# Function to update the datastore to a new workspace
def update_datastore(workspace, datastore, datastore_info):
    # remove workspace field from the datastore_info
    if 'workspace' in datastore_info['dataStore']:
        del datastore_info['dataStore']['workspace']

    url = f'{GEOSERVER_URL}/workspaces/{workspace}/datastores/{datastore}.json'
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, auth=HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD), headers=headers, json=datastore_info)
    if response.status_code in [200, 201]:
        print(f"Successfully moved datastore '{datastore}' to workspace '{workspace}'.")
    else:
        print(f"Failed to move datastore. Status code: {response.status_code} Response: {response.text}")


def update_layer(workspace, layer):
    url = f'{GEOSERVER_URL}/layers/{layer}.json'
    layer_info = {
        "layer": {
            "workspace": {
                "name": workspace
            }
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, auth=HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD),
                            headers=headers, json=layer_info)
    if response.status_code in [200, 201]:
        print(f"Successfully moved layer '{layer}' to workspace '{workspace}'.")
    else:
        print(f"Failed to move layer. Status code: {response.status_code}")


def main():
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    source_workspace = 'incore'

    for dataset in collection.find():
        owner = dataset['owner']
        dataset_id = str(dataset['_id'])

        # Create a new workspace for the user
        create_workspace(owner)

        # there might be two different way.
        # the first one is to use the space db and using the dataset id belongs to each user's space
        # the second one is to iterate the dataset and check the owner field then move
        # the layer to the user's workspace

        # use the second method
        the_method = 2

        # this is test for the first way, and it needs to be changed
        # Iterate over each user in the MongoDB collection
        # Move each layer to the user's workspace
        if the_method == 1:
            for layer_name in dataset_id:
                move_layer_to_workspace(layer_name, 'INCORE', owner)

        # in here, testing the second way now.
        # if the_method == 2:
        #     change_workspace(source_workspace, owner, dataset_id)

    # close the MongoDB connection
    client.close()


if __name__ == "__main__":
    main()
    