#!/usr/bin/env python3

"""
import data from webdav (earthquake.ncsa.illinois.edu) and
store them to incore2 data repository
"""

import hashlib
import os
import shutil
import tempfile

import json
import requests
import urllib
from bs4 import BeautifulSoup
from bson import ObjectId
from mimetypes import MimeTypes
from pymongo import MongoClient
from urllib.request import urlretrieve

from webdav_datasets import MvzDataset, Dataset, FileDescriptor


def main():
    webdav_url = "https://earthquake.ncsa.illinois.edu/"
    prop_dir = "ergo-repo/properties/"
    ds_dir = "ergo-repo/datasets/"
    space_name = "ergo"
    mvz_ext = "mvz"
    # following parameters should be set before running the process. See README.md
    rest_url = ""
    mongo_url = ""
    data_repo_dir = ""

    dir_content_list = get_directory_content(webdav_url + ds_dir)

    # get mvz file
    for tmp_url in dir_content_list:
        mvz_dir_url = webdav_url + prop_dir + tmp_url
        mvz_url_list = get_directory_content(mvz_dir_url)
        for mvz_file_name in mvz_url_list:
            file_name_base, file_ext = os.path.splitext(mvz_file_name)
            # get only mvz files
            if (file_ext == "." + mvz_ext):
                if (file_name_base == "Shelby_County%2C_TN_Boundary1212593366993"):
                    # there is a problem in automatic upload for "Shelby_County%2C_TN_Boundary1212593366993"
                    # due to the cooma character in the name, so it will be hard coded in here
                    print("processing Shelby_County_TN_Boundary1212593366993")
                    file_name_base = "Shelby_County,_TN_Boundary1212593366993"
                    mvz_file_name = "Shelby_County,_TN_Boundary1212593366993.mvz"

                # download mvz file in temp folder
                mvz_url = webdav_url + prop_dir + tmp_url + mvz_file_name
                tmp_mvz_dir = tempfile.mkdtemp()
                mvz_xml_file = urlretrieve(mvz_url, os.path.join(str(tmp_mvz_dir), mvz_file_name))
                mvz_dataset = MvzDataset(mvz_xml_file[0])

                # create FileDescriptor for MvzDataset
                fd = create_mvz_file_descriptor(data_repo_dir, mvz_xml_file[0])
                file_descriptors = []
                file_descriptors.append(fd)
                mvz_dataset.set_file_descriptors(file_descriptors)

                # insert mvz dataset to mongodb
                mvz_id = insert_mvzdataset_to_mongodb(mongo_url, mvz_dataset)

                download_file_urls = []
                downloaded_files = []
                # download_file_urls.append(mvz_url);

                ds_id_file_dir = webdav_url + ds_dir + "/" + tmp_url + "/" + file_name_base + "/converted/"
                ds_id_file_dir_content = get_directory_content(ds_id_file_dir)

                # create a list of the files to download
                for ds_id_file in ds_id_file_dir_content:
                    ds_name_base, ds_ext = os.path.splitext(ds_id_file)
                    file_path, file_name = os.path.split(ds_id_file)
                    downloaded_file = None
                    downloaded_file_name = None
                    if (len(ds_ext) > 0):
                        ds_file_url = ds_id_file_dir + ds_id_file
                        download_file_urls.append(ds_file_url)
                        downloaded_file_name = os.path.join(str(tmp_mvz_dir), file_name)
                        downloaded_files.append(downloaded_file_name)
                        downloaded_file = urlretrieve(ds_file_url, downloaded_file_name)

                # create dataset
                dataset = create_dataset_from_mvz_dataset(mvz_dataset, 'ergo')

                # post the dataset to rest api and get dataset it
                dataset_id = post_dataset_to_repo(dataset, rest_url)

                # upload files for the new dataset
                post_files_to_dataset(dataset_id, downloaded_files, rest_url)

                shutil.rmtree(tmp_mvz_dir)


"""
create FileDescriptor object
"""
def create_mvz_file_descriptor(data_repo_dir, mvz_file_name):
    fd = FileDescriptor()
    new_id = ObjectId()
    new_id = str(new_id)
    fd.set_id(new_id)

    # create folder
    levels = 2
    path = ''
    i = 0
    while (i < levels * 2 and len(new_id) >= i + 2):
        path = path + new_id[i: i + 2] + os.sep
        i = i + 2

    if (len(new_id) > 0):
        path = path + new_id + os.sep

    path = data_repo_dir + os.sep + path

    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.isfile(mvz_file_name):
        shutil.copy(mvz_file_name, path)

    mvz_file = path + os.path.basename(mvz_file_name)
    fd.set_data_url('file:' + os.sep + mvz_file)

    fd.set_filename(os.path.basename(mvz_file_name))

    mime = MimeTypes()
    mime_type = mime.guess_type(urllib.request.pathname2url(mvz_file_name))
    if mime_type[0] == None:
        fd.set_mime_type('application/octet-stream')
    else:
        fd.set_mime_type(mime_type[0])

    mvz_stat = os.stat(mvz_file_name)
    fd.set_size(mvz_stat.st_size)

    hash_md5 = hashlib.md5()
    with open(mvz_file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    fd.set_md5sum(hash_md5.hexdigest())

    return fd


"""
post files and attache them to dataset using file descriptor
"""
def post_files_to_dataset(id, downloaded_files, url):
    url = url + id + "/files"
    files = []
    open_files = []
    for i in range(len(downloaded_files)):
        open_files.append(open(downloaded_files[i], 'rb'))
    for i in range(len(downloaded_files)):
        tuple = ('file', open_files[i])
        files.append(tuple)

    r = requests.post(url, files=files)

    # close downloaded files
    for i in range(len(downloaded_files)):
        open_files[i].close()


"""
post dataset to rest api and obtain dataset id
"""
def post_dataset_to_repo(dataset, rest_url):
    dataset_json = json.dumps(dataset, default=lambda o: o.__dict__)
    dataset_post_url = rest_url
    # dataset_json = "{ schema: \"test-shapefile\", type: \"http://localhost:8080/semantics/edu.illinois.ncsa.ergo.eq.schemas.buildingInventoryVer4.v1.0\", title: \"test\", format: \"shapefile\", spaces: [\"ywkim\", \"ergo\"] }"
    headers = {'X-Credential-Username': 'ergo'}
    result = requests.post(dataset_post_url, files={'dataset': dataset_json}, headers=headers)
    result_dataset_str = result.content.decode()
    result_dataset_json = json.loads(result_dataset_str)
    new_dataset_id = result_dataset_json['id']

    return new_dataset_id


"""
create dataset from MvzDataset
"""
def create_dataset_from_mvz_dataset(mvz_dataset, space_name):
    dataset = Dataset()
    dataset.set_title(mvz_dataset.get_name())
    dataset.set_data_type(mvz_dataset.get_type_id())
    dataset.set_format(mvz_dataset.get_data_format())
    dataset.set_creator(space_name)
    dataset.set_description(mvz_dataset.get_description())
    dataset.set_data_type(mvz_dataset.get_type_id())
    spaces = []
    spaces.append(space_name)
    dataset.set_spaces(spaces)

    return dataset


"""
get the directory content under input url as list without server address
"""
def get_directory_content(url):
    outlist = []
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    for link in soup.find_all('a'):
        outlist.append(link.get('href'))
    return outlist


"""
returns the directory content as a form of full url
"""
def get_directory_string_as_link(url):
    outlist = []
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    outlist = [os.path.joing(url, node.get('href')) for node in soup.find_all('a') if node.get('href')]

    return outlist


"""
insert MvzDataset into mongodb
"""
def insert_mvzdataset_to_mongodb(mongo_url, mvz_dataset):
    client = MongoClient(mongo_url, 27017)
    db = client['datadb']
    coll = db.MvzDataset

    mvz = json.dumps(mvz_dataset, default=lambda x: x.__dict__)
    mvz = json.loads(mvz)

    id = coll.insert(mvz)

    return id


if __name__ == "__main__":
    main()
