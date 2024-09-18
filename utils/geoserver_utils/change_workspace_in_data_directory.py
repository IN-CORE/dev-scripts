import os
import shutil
import xml.etree.ElementTree as ET

# Define paths
data_dir = r"C:/Users/ywkim/Downloads/geoserver-2.22.4-bin/data_dir"
old_workspace = "incore"  # Existing workspace
new_workspace = "ywkim"  # New workspace
# datastore_name = "66ce2d4ccdfc8b4e6928de45"  # The datastore or coverage store name
datastore_name = "66cf726a81983b19154d60f7"

# Paths for old and new workspace directories
old_workspace_path = os.path.join(data_dir, "workspaces", old_workspace, datastore_name)
new_workspace_path = os.path.join(data_dir, "workspaces", new_workspace, datastore_name)
new_workspace_xml_path = os.path.join(data_dir, "workspaces", new_workspace, "workspace.xml")
new_namespace_xml_path = os.path.join(data_dir, "workspaces", new_workspace, "namespace.xml")

# Paths for old and new data directories
old_data_path = os.path.join(data_dir, "data", old_workspace, datastore_name)
new_data_path = os.path.join(data_dir, "data", new_workspace, datastore_name)


# Function to get the workspace ID from the workspace.xml file
def get_workspace_id(workspace_xml_path):
    tree = ET.parse(workspace_xml_path)
    root = tree.getroot()
    workspace_id = root.find("id").text
    return workspace_id


# Function to get the namespace ID from the namespace.xml file
def get_namespace_id(namespace_xml_path):
    tree = ET.parse(namespace_xml_path)
    root = tree.getroot()
    namespace_id = root.find("id").text
    return namespace_id


# Step 2: Move the datastore/coveragestore directory from the old workspace to the new workspace
def move_datastore_or_coveragestore():
    if not os.path.exists(new_workspace_path):
        shutil.move(old_workspace_path, new_workspace_path)
        print(f"Moved store from {old_workspace_path} to {new_workspace_path}.")
    else:
        print(f"Store already exists at {new_workspace_path}. No move needed.")

    if not os.path.exists(new_data_path):
        shutil.move(old_data_path, new_data_path)
        print(f"Moved data from {old_data_path} to {new_data_path}.")
    else:
        print(f"Data already exists at {new_data_path}. No move needed.")


# Step 3: Edit the datastore.xml or coveragestore.xml with the new workspace ID and update the path
def update_store_xml():
    datastore_xml_path = os.path.join(new_workspace_path, "datastore.xml")
    coveragestore_xml_path = os.path.join(new_workspace_path, "coveragestore.xml")

    if os.path.exists(datastore_xml_path):
        update_datastore_xml(datastore_xml_path)
    elif os.path.exists(coveragestore_xml_path):
        update_coveragestore_xml(coveragestore_xml_path)
    else:
        print(f"Neither datastore.xml nor coveragestore.xml found in {new_workspace_path}.")


def update_datastore_xml(datastore_xml_path):
    # Get the new workspace ID
    new_workspace_id = get_workspace_id(new_workspace_xml_path)

    tree = ET.parse(datastore_xml_path)
    root = tree.getroot()

    # Update the workspace ID
    workspace = root.find(".//workspace/id")
    if workspace is not None:
        workspace.text = new_workspace_id

    # Update the namespace URI
    namespace = root.find(".//entry[@key='namespace']")
    if namespace is not None:
        namespace.text = f"http://{new_workspace}"

    # Update the datastore's URL to point to the new path
    url_entry = root.find(".//entry[@key='url']")
    if url_entry is not None:
        corrected_datastore_path = new_data_path.replace("\\", "/")
        url_entry.text = f"file:/{corrected_datastore_path}/"

    # Save the updated XML
    tree.write(datastore_xml_path)
    print(f"Updated {datastore_xml_path} with new workspace ID and namespace.")


def update_coveragestore_xml(coveragestore_xml_path):
    # Get the new workspace ID
    new_workspace_id = get_workspace_id(new_workspace_xml_path)

    tree = ET.parse(coveragestore_xml_path)
    root = tree.getroot()

    # Update the workspace ID
    workspace = root.find(".//workspace/id")
    if workspace is not None:
        workspace.text = new_workspace_id

    # Update the coveragestore's URL to point to the new relative path
    url_entry = root.find(".//url")
    if url_entry is not None:
        relative_path = os.path.join("data", new_workspace, datastore_name, os.path.basename(url_entry.text))
        relative_path = relative_path.replace("\\", "/")
        url_entry.text = f"file:{relative_path}"

    # Save the updated XML
    tree.write(coveragestore_xml_path)
    print(f"Updated {coveragestore_xml_path} with new workspace ID and path.")


# Step 4: Edit all layers' featuretype.xml or coverage.xml with the new namespace ID
def update_layer_xml():
    # Get the new namespace ID
    new_namespace_id = get_namespace_id(new_namespace_xml_path)

    for layer_dir in os.listdir(new_workspace_path):
        featuretype_xml_path = os.path.join(new_workspace_path, layer_dir, "featuretype.xml")
        coverage_xml_path = os.path.join(new_workspace_path, layer_dir, "coverage.xml")

        if os.path.exists(featuretype_xml_path):
            update_featuretype_xml(featuretype_xml_path, new_namespace_id)
        elif os.path.exists(coverage_xml_path):
            update_coverage_xml(coverage_xml_path, new_namespace_id)
        else:
            print(f"Neither featuretype.xml nor coverage.xml found in {layer_dir}.")


def update_featuretype_xml(featuretype_xml_path, new_namespace_id):
    tree = ET.parse(featuretype_xml_path)
    root = tree.getroot()

    # Update the namespace ID
    namespace = root.find(".//namespace/id")
    if namespace is not None:
        namespace.text = new_namespace_id

    # Save the updated XML
    tree.write(featuretype_xml_path)
    print(f"Updated {featuretype_xml_path} with new namespace ID.")


def update_coverage_xml(coverage_xml_path, new_namespace_id):
    tree = ET.parse(coverage_xml_path)
    root = tree.getroot()

    # Update the namespace ID
    namespace = root.find(".//namespace/id")
    if namespace is not None:
        namespace.text = new_namespace_id

    # Save the updated XML
    tree.write(coverage_xml_path)
    print(f"Updated {coverage_xml_path} with new namespace ID.")


# Run the steps
move_datastore_or_coveragestore()
update_store_xml()
update_layer_xml()

print("Store and layers updated successfully.")
