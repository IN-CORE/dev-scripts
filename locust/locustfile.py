import json
from urllib.parse import urljoin

from locust import HttpUser, task, between


class MyUser(HttpUser):
    wait_time = between(1, 5)  # Add the desired wait time between tasks
    headers = {"content-type" : "application/x-www-form-urlencoded", "Authorization": "bearer {Your Authenication}"}

    @task
    def hazard(self):
        earthquake_id = "5b902cb273c3371e1236b36b";

        form_data = {
           "name":"yytest",
           "description":"yytest",
           "eqType":"model",
           "attenuations":{
              "ChiouYoungs2014":"1.0"
           },
           "eqParameters":{
              "srcLatitude":40.177,
              "srcLongitude":-111.426,
              "magnitude":"5.5",
              "depth":"11.2",
              "region":"",
              "faultTypeMap":{
                 "ChiouYoungs2014":"Normal"
              }
           },
           "visualizationParameters":{
              "demandType":"PGA",
              "demandUnits":"g",
              "minX":-112.312,
              "minY":40.277,
              "maxX":-111.462,
              "maxY":41,

              "numPoints":"1025",
              "amplifyHazard":"true"
           }
        }

        context = """
                {
           "name":"yytest",
           "description":"yytest",
           "eqType":"model",
           "attenuations":{
              "ChiouYoungs2014":"1.0"
           },
           "eqParameters":{
              "srcLatitude":40.177,
              "srcLongitude":-111.426,
              "magnitude":"5.5",
              "depth":"11.2",
              "region":"",
              "faultTypeMap":{
                 "ChiouYoungs2014":"Normal"
              }
           },
           "visualizationParameters":{
              "demandType":"PGA",
              "demandUnits":"g",
              "minX":-112.312,
              "minY":40.277,
              "maxX":-111.462,
              "maxY":41,
             
              "numPoints":"1025",
              "amplifyHazard":"true"
           }
        }
        """


        self.client.get(f"hazard/api/earthquakes/{earthquake_id}", headers=self.headers)
        #self.client.post("hazard/api/earthquakes/", json=json.dumps(form_data), headers=self.headers)



    @task
    def dataset(self):
        self.client.get("data/api/datasets/5d07cbe9b9219c065b819103", headers=self.headers)
        self.client.get("data/api/datasets/5dbc8478b9219c06dd242c0d", headers=self.headers)
        self.client.get("data/api/datasets/60fb4241544e944c3cedb507", headers=self.headers)
        self.client.get("data/api/datasets/60fb411060b3f4124301f95a", headers=self.headers)
        self.client.get("data/api/datasets/60fb433cd3c92a78c89d21cc", headers=self.headers)
        self.client.get("data/api/datasets/64ee0bcd553ecf0768e21e55", headers=self.headers)
