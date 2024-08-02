"""
This script performs a stress test against various in-core services.
The services include:
1. Geoserver (handling both vector and raster datasets)
2. Data services
3. DFR3 services
4. Hazard services, which encompass the following operations:
   a. Fetch hazard
   b. Create model-based hazard
   c. Create dataset-based hazard
   d. Update hazard values
"""

import json
import logging
import mimetypes
import time
from http.client import HTTPConnection
from locust import HttpUser, task, between
from codecs import encode


class MyUser(HttpUser):
    wait_time = between(1, 5)  # Add the desired wait time between tasks

    headers = {
        "Authorization": ""
    }

    ##### Debugging #####
    # HTTPConnection.debuglevel = 1
    # logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)
    # requests_log = logging.getLogger("requests.packages.urllib3")
    # requests_log.setLevel(logging.DEBUG)
    # requests_log.propagate = True

    @task
    def geoserver(self):
        # joplin building inventory
        self.client.get("/geoserver/incore/wms?service=WMS&version=1.1.0&request=GetMap&layers=incore%3A60622b01c57ada48e48d7013&bbox=-94.58364094982268%2C37.01554491871878%2C-94.40576902948776%2C37.14723277660234&width=768&height=568&srs=EPSG%3A4326&styles=&format=image/png")

        # raster
        self.client.get("/geoserver/incore/wms?service=WMS&version=1.1.0&request=GetMap&layers=incore%3A5f4d02e352147a614c71960b&bbox=-79.212607077%2C34.562496808%2C-78.973249171%2C34.705963648&width=768&height=460&srs=EPSG%3A4326&styles=&format=image/png")

    @task
    def dataset(self):
        # Get tornado dataset (60a44ae8605f0462bd4263ac)
        self.client.get("/data/api/datasets/60a44ae77da24b7b5ba0e86f", headers=self.headers)

        # Get building dataset (5dbc8478b9219c06dd242c0d)
        self.client.get("/data/api/datasets/5dbc8478b9219c06dd242c0d", headers=self.headers)

        # Get socio_demographic_data = "60fb4241544e944c3cedb507"
        self.client.get("/data/api/datasets/60fb4241544e944c3cedb507", headers=self.headers)

        # Get financial_resources = "60fb411060b3f4124301f95a"
        self.client.get("/data/api/datasets/60fb411060b3f4124301f95a", headers=self.headers)

        # Get delay_factors = "60fb433cd3c92a78c89d21cc"
        self.client.get("/data/api/datasets/60fb433cd3c92a78c89d21cc", headers=self.headers)

        # Get 64ee0bcd553ecf0768e21e55
        self.client.get("/data/api/datasets/64ee0bcd553ecf0768e21e55", headers=self.headers)

    @task
    def dfr3(self):
        # GET /fragilities/{id}
        self.client.get("/dfr3/api/fragilities/5b47b2d7337d4a36187c61c9", headers=self.headers)

        # GET /mappings/{id}
        self.client.get("/dfr3/api/mappings/5b47b2d9337d4a36187c7564", headers=self.headers)

        # GET /repairs/{id}
        self.client.get("/dfr3/api/repairs/6513058862ba036575da5fca", headers=self.headers)

    @task
    def hazard_earthquake(self):
        id = "5b902cb273c3371e1236b36b";
        url = "/hazard/api/earthquakes/"
        earthquake_model_json = {
            "name": "Memphis EQ Model (modified)",
            "description": "Memphis model based hazard",
            "eqType": "model",
            "attenuations": {
                "AtkinsonBoore1995": "1.0"
            },
            "eqParameters": {
                "srcLatitude": "35.927",
                "srcLongitude": "-89.919",
                "magnitude": "8.1",
                "depth": "7.0"
            },
            "visualizationParameters": {
                "demandType": "PGA",
                "demandUnits": "g",
                "minX": "-90.3099",
                "minY": "34.9942",
                "maxX": "-89.6231",
                "maxY": "35.4129",
                "numPoints": "1025",
                "amplifyHazard": "true"
            }
        }
        earthquake_dataset_json = {
            "name": "Memphis Deterministic EQ",
            "description": "Memphis dataset based deterministic hazard",
            "eqType": "dataset",
            "hazardDatasets": [
                {
                    "hazardType": "deterministic",
                    "demandType": "SA",
                    "demandUnits": "g",
                    "period": "0.2",
                    "eqParameters": {
                        "srcLatitude": "35.927",
                        "srcLongitude": "-89.919",
                        "magnitude": "7.9",
                        "depth": "10.0"
                    }
                },
                {
                    "hazardType": "deterministic",
                    "demandType": "PGA",
                    "demandUnits": "g",
                    "period": "0.0",
                    "eqParameters": {
                        "srcLatitude": "35.927",
                        "srcLongitude": "-89.919",
                        "magnitude": "7.9",
                        "depth": "10.0"
                    }
                }
            ]
        }
        points = """[
            {
                "demands": ["0.2 SA"],
                "units": ["g"],
                "loc": "35.07899, -90.0178"
            },
            {
                "demands": ["0.2 SA", "PGA", "0.8 SA"],
                "units": ["g", "g", "g"],
                "loc": "35.027, -90.077"
            }
        ]"""

        files = [
            {"name": "eq-dataset-SA.tif",
             "location": "/Users/ylyang/incore-workshop/inspire-workshop-2023-11-15/session2/data/hazard/earthquake/eq-dataset-SA.tif"},
            {"name": "eq-dataset-PGA.tif",
             "location": "/Users/ylyang/incore-workshop/inspire-workshop-2023-11-15/session2/data/hazard/earthquake/eq-dataset-PGA.tif"}
        ]

        # GET /earthquakes/{id}
        self.client.get(f"{url}{id}", headers=self.headers)

        # POST /earthquake for model based
        self.post_hazard_model(url, self.headers, earthquake_model_json, "earthquake")

        # POST /earthquake for dataset based
        self.post_hazard_dataset(url, self.headers, earthquake_dataset_json, "earthquake", files)

        # POST /earthquakes/{id}/values
        self.post_hazard_values(url, id, self.headers, points)

    @task
    def hazard_tornado(self):
        id = "60a44ae8605f0462bd4263ac";
        url = "/hazard/api/tornadoes/"
        tornado_json_model = {
            "name": "Centerville Model Tornado (modified)",
            "description": "Centerville mean width tornado hazard",
            "tornadoType": "model",
            "tornadoModel": "MeanWidthTornado",
            "tornadoParameters": {
                "efRating": "EF4",
                "startLatitude": "35.215",
                "startLongitude": "-97.524",
                "randomSeed": "3457",
                "endLatitude": [35.253],
                "endLongitude": [-97.432],
                "windSpeedMethod": "1",
                "numSimulations": "1"
            }
        }
        tornado_json_dataset = {
            "name": "Joplin Dataset Tornado - workshop",
            "description": "Joplin tornado hazard with shapefile",
            "tornadoType": "dataset"
        }
        points = """[
            {
                "demands": ["wind"],
                "units": ["mph"],
                "loc": "35.215, -97.521"
            },
            {
                "demands": ["wind"],
                "units": ["mph"],
                "loc": "35.215, -97.519"
            }
        ]"""
        files = [
            {"name": "joplin_path_wgs84.shp",
             "location": "/Users/ylyang/incore-workshop/inspire-workshop-2023-11-15/session2/data/hazard/tornado/joplin_path_wgs84.shp"},
            {"name": "joplin_path_wgs84.dbf",
             "location": "/Users/ylyang/incore-workshop/inspire-workshop-2023-11-15/session2/data/hazard/tornado/joplin_path_wgs84.dbf"},
            {"name": "joplin_path_wgs84.shx",
             "location": "/Users/ylyang/incore-workshop/inspire-workshop-2023-11-15/session2/data/hazard/tornado/joplin_path_wgs84.shx"},
            {"name": "joplin_path_wgs84.prj",
             "location": "/Users/ylyang/incore-workshop/inspire-workshop-2023-11-15/session2/data/hazard/tornado/joplin_path_wgs84.prj"}
        ]

        # GET /tornadoes/{id}
        self.client.get(f"{url}{id}", headers=self.headers)

        # POST /tornadoes for model based
        self.post_hazard_model(url, self.headers, tornado_json_model, "tornado")

        # POST /tornadoes for dataset based
        self.post_hazard_dataset(url, self.headers, tornado_json_dataset, "tornado", files)

        # POST /tornadoes/{id}/values
        self.post_hazard_values(url, id, self.headers, points)

    def post_hazard_model(self, url, headers, form_data, hazard):
        dataList = []
        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
        dataList = self.add_text(dataList, hazard, form_data, boundary)

        dataList.append(encode('--' + boundary + '--'))
        dataList.append(encode(''))

        body = b'\r\n'.join(dataList)
        payload = body
        headers = headers | {'Content-type': 'multipart/form-data; boundary={}'.format(boundary)}

        res = self.client.post(f"{url}", data=payload, headers=headers)
        if res.status_code == 200:
            index = 0
            is_space_ok = False
            while is_space_ok is False and index <= 5:
                time.sleep(5)
                id = res.json()['id']
                get_res = self.client.get(f"{url}{id}", headers=headers)
                index += 1

                if get_res.status_code == 200:
                    is_space_ok = True
                    self.client.delete(f"{url}{id}", headers=headers)

    def post_hazard_dataset(self, url, headers, form_data, hazard, files):
        dataList = []
        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
        dataList = self.add_text(dataList, hazard, form_data, boundary)

        for file in files:
            dataList = self.add_file(dataList, file, boundary)

        dataList.append(encode('--' + boundary + '--'))
        dataList.append(encode(''))
        body = b'\r\n'.join(dataList)
        payload = body
        headers = headers | {'Content-type': 'multipart/form-data; boundary={}'.format(boundary)}

        res = self.client.post(f"{url}", data=payload, headers=headers)
        if res.status_code == 200:
            index = 0

            is_space_ok = False
            while is_space_ok is False and index <= 5:
                time.sleep(5)
                id = res.json()['id']
                get_res = self.client.get(f"{url}{id}", headers=headers)
                index += 1

                if get_res.status_code == 200:
                    is_space_ok = True
                    self.client.delete(f"{url}{id}", headers=headers)

    def post_hazard_values(self, url, id, headers, form_data):
        dataList = []
        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name=points;'))

        dataList.append(encode('Content-Type: {}'.format('text/plain')))
        dataList.append(encode(''))

        dataList.append(encode(form_data))
        dataList.append(encode('--' + boundary + '--'))
        dataList.append(encode(''))
        body = b'\r\n'.join(dataList)
        payload = body
        headers = headers | {'Content-type': 'multipart/form-data; boundary={}'.format(boundary)}

        self.client.post(f"{url}{id}/values", data=payload, headers=headers)

    def add_text(self, dataList, key, form_data, boundary):
        dataList.append(encode('--' + boundary))
        dataList.append(encode(f'Content-Disposition: form-data; name={key};'))
        dataList.append(encode('Content-Type: {}'.format('text/plain')))
        dataList.append(encode(''))
        dataList.append(encode(json.dumps(form_data)))
        return dataList

    def add_file(self, dataList, file, boundary):
        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format(file.get("name"))))
        fileType = mimetypes.guess_type(file.get("location"))[0] or 'application/octet-stream'
        dataList.append(encode('Content-Type: {}'.format(fileType)))
        dataList.append(encode(''))
        with open(file.get("location"), 'rb') as f:
            dataList.append(f.read())

        return dataList
