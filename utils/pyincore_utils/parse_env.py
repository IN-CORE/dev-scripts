import yaml
import os
from collections import defaultdict
from typing import Tuple, Optional

# def env files names:

UBUNTU_ENV_FILE = 'env-' # ubuntu env files
MAC_ENV_FILE = 'mac-env-' # mac env files
WIN_ENV_FILE = 'win-env-' # windows env files

# python versions

PYTHON_V = [
    # 'py38.yml', # dropping support for python 3.8 because of numpy clashes
    'py39.yml',
    'py310.yml',
    'py311.yml',
]

pyincore_req_packages = [
    "fiona",
    "geopandas",
    "matplotlib",
    "networkx",
    "numpy",
    "pandas",
    "pycodestyle",
    "pyomo",
    "pyproj",
    "pytest",
    "python-jose",
    "rasterio",
    "requests",
    "rtree",
    "scipy",
    "shapely",
]

def get_yaml_file(py_v: str) -> Tuple[Optional[dict], Optional[dict], Optional[dict]]:
    '''
    Get the yaml file for the python version.
    '''
    lin_yml = None
    mac_yml = None
    win_yml = None
    if os.path.exists((UBUNTU_ENV_FILE + py_v)):
        with open(UBUNTU_ENV_FILE + py_v, 'r') as f:
            lin_yml = yaml.safe_load(f)
    
    if os.path.exists((MAC_ENV_FILE + py_v)):
        with open(MAC_ENV_FILE + py_v, 'r') as f:
            mac_yml = yaml.safe_load(f)
    
    if os.path.exists((WIN_ENV_FILE + py_v)):
        with open(WIN_ENV_FILE + py_v, 'r') as f:
            win_yml = yaml.safe_load(f)
    
    return lin_yml, mac_yml, win_yml

def get_min_dep() -> dict:
    '''
    Get the minimum dependencies for the project. across platform for various packages.
    '''

    ver_list = defaultdict(list)
    for py_v in PYTHON_V:
        # get all the yaml files for the python version
        lin_yml, mac_yml, win_yml = get_yaml_file(py_v)
        
        # get the dependencies for each platform listed in requirements
        lin_deps = dict([(dep.split("=")[0], dep.split("=")[1]) for dep in lin_yml['dependencies'] if dep.split("=")[0] in pyincore_req_packages]) if lin_yml else {}
        mac_deps = dict([(dep.split("=")[0], dep.split("=")[1]) for dep in mac_yml['dependencies'] if dep.split("=")[0] in pyincore_req_packages]) if mac_yml else {}
        win_deps = dict([(dep.split("=")[0], dep.split("=")[1]) for dep in win_yml['dependencies'] if dep.split("=")[0] in pyincore_req_packages]) if win_yml else {}
        
        
        for pyincore_pkg in pyincore_req_packages:
            if pyincore_pkg in lin_deps:
                ver_list[pyincore_pkg].append(lin_deps[pyincore_pkg])
            if pyincore_pkg in mac_deps:
                ver_list[pyincore_pkg].append(mac_deps[pyincore_pkg])
            if pyincore_pkg in win_deps:
                ver_list[pyincore_pkg].append(win_deps[pyincore_pkg])

    # get the minimum version for each package
    min_ver = {}
    for pkg, ver in ver_list.items():
        min_ver[pkg] = min(ver)
    
    return min_ver


if __name__ == '__main__':
    min_deps = get_min_dep()
    with open("requirements.min", "w") as f:
        for pkg, ver in min_deps.items():
            f.write(f"{pkg}>={ver}\n")
        

