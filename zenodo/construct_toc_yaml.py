import os
import json
import yaml

ZENODO_DIR = "zenodo_downloads"  # the folder where downloaded zip files exists
TOC_FILE = "_toc.yml"


def load_index_files(zenodo_dir=ZENODO_DIR):
    """Loads index.json files from all first-level subfolders in"""
    index_data = {}

    for folder in os.listdir(ZENODO_DIR):
        folder_path = os.path.join(ZENODO_DIR, folder)
        index_file = os.path.join(folder_path, "index.json")

        if os.path.isdir(folder_path) and os.path.exists(index_file):
            with open(index_file, "r") as f:
                try:
                    index_data[folder] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading {index_file}. Ensure it has valid JSON.")

    return index_data


def build_toc_structure(index_data):
    """Constructs the hierarchical structure for _toc.yml based on the parent field"""
    toc_structure = {"format": "jb-book", "root": "introduction.md", "defaults": {"numbered": False}, "chapters": []}
    parent_map = {}  # Maps parents to their children

    # Parse the index.json files and group by parent
    for folder, data in index_data.items():
        top_level_parent = data["parent"]
        entries = data["entries"]

        # Ensure the top-level parent is represented as a markdown file in chapters. e.g. notebooks, tutorials,
        # workshops
        if top_level_parent:
            top_level_entry = {"file": f"{top_level_parent}.md"}
            if top_level_entry not in toc_structure["chapters"]:
                toc_structure["chapters"].append(top_level_entry)

        for entry in entries:
            file_entry = {"file": entry["file"]}

            # If it has a parent, store in a map for later processing
            if entry["parent"]:
                if entry["parent"] not in parent_map:
                    parent_map[entry["parent"]] = []
                parent_map[entry["parent"]].append(file_entry)
            else:
                # Place the file under its top-level parent instead of the root
                if top_level_parent not in parent_map:
                    parent_map[top_level_parent] = []
                parent_map[top_level_parent].append(file_entry)

    # Recursively assign child sections
    def assign_sections(parent_entry):
        parent_key = os.path.splitext(parent_entry["file"])[0]
        if parent_key in parent_map:
            parent_entry["sections"] = parent_map[parent_key]
            for child in parent_entry["sections"]:
                assign_sections(child)

    # Attach sections to top-level parents
    for chapter in toc_structure["chapters"]:
        assign_sections(chapter)

    return toc_structure


def save_toc_file(toc_structure, toc_file_path=TOC_FILE):
    """Writes the constructed TOC structure to _toc.yml"""
    with open(toc_file_path, "w") as f:
        yaml.dump(toc_structure, f, default_flow_style=False, sort_keys=False)
    print(f"✅ Successfully generated {toc_file_path}")


if __name__ == "__main__":
    index_data = load_index_files()
    toc_structure = build_toc_structure(index_data)
    save_toc_file(toc_structure)
