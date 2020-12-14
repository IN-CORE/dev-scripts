import glob

# TODO install python in geoserver pod
#  https://websiteforstudents.com/installing-the-latest-python-3-7-on-ubuntu-16-04-18-04/
#  https://pip.pypa.io/en/stable/installing/
# BASE_DIR = "/opt/geoserver/data_dir/workspaces/incore/"
BASE_DIR = "C:\\Users\\ywkim\\Downloads\\Tmp\\geoserver_test\\"
FIND_STR = '/home/geoserver/data_dir/'
REPLACE_STR = '/opt/geoserver/data_dir/'
# FIND_STR = 'http://incore2-geoserver.ncsa.illinois.edu'
# REPLACE_STR = 'https://incore-tst.ncsa.illinois.edu'

def main():
    # there are coveragestore.xml and datastore.xml
    search_dir = BASE_DIR + "*\\*.xml"
    xml_files = []
    for file in glob.glob(search_dir):
        xml_files.append(file)

    total = len(xml_files)
    for index, file in enumerate(xml_files):
        in_file = open(file, "rt")
        data = in_file.read()
        data = data.replace(FIND_STR, REPLACE_STR)
        in_file.close()
        in_file = open(file, "wt")
        in_file.write(data)
        in_file.close()
        print(str(total - index) + " iterations left")


if __name__ == '__main__':
    main()