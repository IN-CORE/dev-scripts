"""
This script performs a stress test against community app.
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
        'Content-Type': 'application/json',
        'Authorization': ''
    }

    ##### Debugging #####
    # HTTPConnection.debuglevel = 1
    # logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)
    # requests_log = logging.getLogger("requests.packages.urllib3")
    # requests_log.setLevel(logging.DEBUG)
    # requests_log.propagate = True

    @task
    def post_retrofit_strategy(self):
        url = "https://incore.ncsa.illinois.edu/datawolf/executions/"
        # response Content-Type: text/plain
        # request Content-Type: application/json
        payload = json.dumps(
            {"workflowId": "efc14b0f-1848-4dc7-ad0d-69ef6d7f0d9c", "creatorId": "59108b8c-e409-4877-82f7-0dbf729fa539",
             "title": "Test", "description": "", "parameters": {
                "e9e3afdf-3af4-49d3-a0a6-70de8c177574": "{\"testbed\":\"galveston\",\"rules\":1,\"zones\":[\"1p\"],\"strtypes\":[\"2\"],\"pcts\":[50]}",
                "ce6a1f7e-4b0d-40bc-b36b-68a0e43c66be": "{\"ret_keys\":[\"elevation\"],\"ret_vals\":[5]}",
                "cb0c76c0-f5ef-4e14-c4ef-bf4205711003": "Test",
                "c67ef86a-568f-46dd-aced-3cdaa851da97": "https://incore.ncsa.illinois.edu",
                "bb8ebbaf-3c76-417c-8ffe-fad2d574ec48": "galveston-app"},
             "datasets": {"89ac4a5b-7da1-4689-c5cc-a9607229f1b3": "4bf920c4-8ecc-4f81-820a-8f121918cc65"}})

        res = self.client.post(url, data=payload, headers=self.headers)

        # The code below is intended to delete test data, but there is no straightforward way to remove the test data
        # so I comment it out
        # if res.status_code == 200:
        #     index = 0
        #     is_space_ok = False
        #     while is_space_ok is False and index <= 5:
        #         time.sleep(5)
        #         id = res
        #         get_res = self.client.get(f"{url}{id}", headers=self.headers)
        #         index += 1
        #
        #         if get_res.status_code == 200:
        #             is_space_ok = True
        #              self.client.delete(f"{url}{id}", headers=self.headers)

    @task
    def post_executions_with_retrofit_strategy(self):
        start_time = time.time()
        url = "https://incore.ncsa.illinois.edu/datawolf/executions/"
        # response Content-Type: text/plain
        # request Content-Type: application/json
        payload = json.dumps(
            {"workflowId": "9c1c11c8-9ba5-4125-bb35-e032095983af", "creatorId": "59108b8c-e409-4877-82f7-0dbf729fa539",
             "title": "Test from Lost", "description": "Test from Lost",
             "parameters": {"103b5143-8059-4052-bb9c-10fb6b956471": "Galveston",
                            "bb421a94-e990-483d-d08f-7b67961eb2b2": "Galveston",
                            "b2ed3ad7-8209-49e5-f25e-bb85527a7bd4": "Galveston",
                            "ab39eb9c-7110-4d62-90a5-0cdbf23c07de": "Galveston",
                            "f0387d6d-1e3e-426e-89b5-6351f84eaef6": "Galveston",
                            "c68e32f3-06fc-4a61-e701-4abb3e8f5281": "Galveston",
                            "1c7a6d9c-3d5c-4020-b1ba-c7feee3f4ef6": "Galveston",
                            "db1d7f2b-be47-41f1-87f6-d4624e0c8de9": "Galveston",
                            "ecc1d35f-3a34-46d9-e306-dc8bc5738eed": "Galveston",
                            "ffca1ace-2264-4dbe-e7c8-ecedc2dc748b": "Galveston",
                            "35ddf87b-7eb4-4b5f-d606-b0d73fb904cc": "Galveston",
                            "15e42c27-cec2-471e-a231-0938a461c9ea": "Galveston",
                            "be9266c0-6fc5-4861-9844-9c31d7bf2c78": "Galveston",
                            "5a644796-4ea5-447d-8ff4-70f34dc5548b": "Galveston",
                            "ea439f27-c1aa-4103-d10a-b55ba8c82912": "Galveston",
                            "59b0b59b-db87-408f-9d40-2103af92d74b": "Galveston",
                            "419c1e2c-3e8e-4354-e883-e0f4d49576c5": "Galveston",
                            "cbec56c7-c1c7-4dd3-bb9c-f0834c4bd70a": "Galveston",
                            "59331924-949f-4c78-ffa1-706f4ed0b6f3": "Galveston",
                            "d1b0b142-b755-4ad7-8959-ba1ffe9b2864": "DS_0 DS_1 DS_2 DS_3",
                            "2d42149f-dee4-4888-d26c-f4150bfd62c3": "DS_0 DS_1 DS_2 DS_3 DS_4",
                            "f94aea0f-4276-48e6-8f1e-dd6b1eb3ce78": "DS_2 DS_3",
                            "433418a3-10b6-42e7-e947-bc2a4a9f7334": "DS_2 DS_3 DS_4",
                            "85105a63-8cba-408d-de57-57d57f7742e4": 1111, "03d4fe6f-d9d6-4bfb-900d-5c17c6a91b49": 1111,
                            "19ee09f2-57dc-4652-9bff-8e5db6758820": 1111, "d109c67d-c547-4d86-da41-12d2b4d389bb": 1111,
                            "cd35e4d1-f2cc-4329-ccd9-6e679f7468ab": 1111, "b6280019-3f7c-45ab-c4ab-f5914ff57416": 1111,
                            "8ecae30f-8a44-4ea2-a62b-e2129559f562": 1111, "a45d5c3a-dd94-4780-a366-adda08b7c9a4": 100,
                            "1fa63fcb-7093-4737-b3a8-0e1fd6c00cac": 100, "72d2212a-9aa6-4511-c0b8-6990e5f51667": 8,
                            "145a7b7c-19f3-40cb-9d7f-3131d8d39d1b": 8, "9eefb251-7b32-4101-823e-1da5f3bfcda5": 8,
                            "937224ee-0e6c-40d7-dd2e-6a40018c1a02": 8, "e588c1a2-9716-41ed-850c-70f626ce0b5a": 8,
                            "1f439687-ddd2-4822-e5e0-40a33860b308": 8, "fa432b67-adb9-47cb-bd0e-aa7197aada15": 8,
                            "5a299c82-de5a-425e-c614-4131f832bfb2": "https://incore.ncsa.illinois.edu",
                            "62a70e86-ae79-42cd-f5a5-58c9cabb2b05": "https://incore.ncsa.illinois.edu",
                            "b9ef16f4-c7ad-4102-d655-3e003d07e19a": "https://incore.ncsa.illinois.edu",
                            "90deb257-9323-47b1-ebb1-08d369a3bf50": "https://incore.ncsa.illinois.edu",
                            "35be8a30-a623-447b-9f2a-cd90155d1638": "https://incore.ncsa.illinois.edu",
                            "ff748e6c-3410-4751-bad4-ff98a7594026": "https://incore.ncsa.illinois.edu",
                            "91b27c64-7508-4414-decb-a44f53f2ff97": "https://incore.ncsa.illinois.edu",
                            "38a0ecc3-6a49-4629-d75d-324d2b7cf79a": "https://incore.ncsa.illinois.edu",
                            "ad3f373b-83a4-4a64-9a52-286989e8fae1": "https://incore.ncsa.illinois.edu",
                            "1199d11d-6354-45af-ec56-3b95c684df3b": "https://incore.ncsa.illinois.edu",
                            "b1d78389-bc45-424e-8310-bd502451fa08": "https://incore.ncsa.illinois.edu",
                            "e58893b5-d7a0-428a-ec04-0965c6b0af0e": "https://incore.ncsa.illinois.edu",
                            "667febc2-6d3b-4c67-bd52-5a678dfa4418": "https://incore.ncsa.illinois.edu",
                            "c4cdeae6-da88-4317-b08b-720d5cf77dd2": "https://incore.ncsa.illinois.edu",
                            "2dd45c06-bc4a-4829-b4a5-84486329e528": "https://incore.ncsa.illinois.edu",
                            "ae37b54d-a49b-4810-85bc-531ef4425bff": "https://incore.ncsa.illinois.edu",
                            "cc1b9842-a4d9-4479-a232-6bccf2fcdabc": "https://incore.ncsa.illinois.edu",
                            "35afa396-03c6-4b47-e3b0-de80120f48a1": "https://incore.ncsa.illinois.edu",
                            "753e2aaa-1f32-4c2d-bade-88ec43c8435c": "https://incore.ncsa.illinois.edu",
                            "9c9e4b0d-28d0-46f8-9288-6a0ce27a1c49": "https://incore.ncsa.illinois.edu",
                            "0d10cacb-6926-46c3-d8a6-f96e2a7f540e": "https://incore.ncsa.illinois.edu",
                            "706184d5-85da-4245-c28e-98fde1bf3150": "hurricane",
                            "a385ac10-a8c4-44e0-8293-75d77d4c3793": "hurricane",
                            "5f4dd770-c0ce-4387-c29b-2316dfa2c437": "hurricane",
                            "32899621-936b-417a-e205-533ed2533654": "hurricane",
                            "69a4732f-c914-40ca-c2ac-f61242bf2190": "5fa5a9497e5cdf51ebf1add2",
                            "71e714b0-fa46-4e39-923c-7c5087665f86": "5fa5a9497e5cdf51ebf1add2",
                            "f187f11f-8ffe-468c-b909-c7c154e8ccf6": "5fa5a9497e5cdf51ebf1add2",
                            "a25766e2-b8d3-45dc-86f1-c8dc86582095": "5fa5a9497e5cdf51ebf1add2",
                            "43c0d905-d219-40c1-a95a-aabbc164f59c": "Non-Retrofit Fragility ID Code",
                            "28e71889-26b7-4178-b3c3-55b71b18d6bc": "", "3e537d73-25c3-4432-e208-88a9a32001ce": "",
                            "f0bc6779-2264-45da-ec0b-e07edda2434a": "", "a0c5a39b-ff11-4898-a2dc-dd5ca139c732": "",
                            "80231a18-429b-43fa-de34-c8ab054b417e": "", "4f2cfa0a-9e3c-4117-c3e1-37eef6d924d1": "",
                            "e119477e-7b01-4447-a5cc-c74e5b2e5fd1": "", "cd604605-3bf0-4bbe-bcc4-dc03806d5db2": "",
                            "e0a8a11f-ed36-49b4-a6e8-a3c92c939bb6": "", "dad935c9-0369-4ca3-ab93-aacaa43885f6": "",
                            "deb73def-173f-4df6-b49f-0716964ebc24": "", "ce7e0bd4-00b0-4c64-8466-30720922d7a9": "",
                            "2cf39637-68c6-4dfb-f953-3494363483cd": "", "5f2b59eb-6041-4389-c13a-fe2d6c5d51ee": "",
                            "c800feb2-8515-4ea6-b52c-817d51c3a271": "", "60df1d7f-cd4e-431e-a8d8-d65bddc33d3a": "",
                            "3f8b0db0-c24b-4cc5-85fc-e9b06b9db485": "63ff6b135c35c0353d5ed3ac",
                            "37cf203f-36c8-4ff7-c2a2-3e67cfca42ec": "63ff6b135c35c0353d5ed3ac",
                            "0d453ac8-fa91-4517-8727-9921ad17c3d1": "63ff6b135c35c0353d5ed3ac",
                            "7a831e75-2a5c-4be9-c792-c4dd8d9fc64d": "63ff6b135c35c0353d5ed3ac",
                            "dcf00197-caa3-44e8-fd33-126c73ea7672": "63ff6b135c35c0353d5ed3ac",
                            "5811164f-aa54-4155-db3d-a8f174785546": "63ff6b135c35c0353d5ed3ac",
                            "34d5e043-f0b9-4ace-d3a3-276429954516": "63ff6b135c35c0353d5ed3ac",
                            "02319e5d-65ac-45b0-a9a5-b033cbbe029a": "63ff6b135c35c0353d5ed3ac",
                            "ade43ab3-8591-47d6-ac39-548fc7749728": "63ff6b135c35c0353d5ed3ac",
                            "0118354a-ef49-4e44-cd07-d73b81180550": "63ff6b135c35c0353d5ed3ac",
                            "905dd2c1-e0bd-412f-fb3b-99533fd1bc70": "63ff6b135c35c0353d5ed3ac",
                            "3091cc60-86cf-44ce-9dcf-2ef2b227aab4": "660ac4db1fb1c519c6fc2999",
                            "36b8c16f-9dc7-4d3e-f1fe-36c978b9f84c": "660ac4db1fb1c519c6fc2999",
                            "1ebbf186-ddba-45b4-c570-0406915a37ab": "",
                            "03bf9f80-8544-464d-c867-d7c0c0c495b4": "62fc000f88470b319561b58d",
                            "9c9956ee-cff1-4f94-8e48-cafad3f898e8": "62fc000f88470b319561b58d",
                            "6cf1350a-b5d8-4921-fed0-35acd1b2ab12": "62fac92ecef2881193f22613",
                            "8739d850-605d-466f-aa1f-7d6069f80932": "1,7,13,25,49,85",
                            "23ce8682-cdfa-4fcd-a335-219a40332e6b": "63d178c2a011a9746c948115",
                            "1eb72116-ce74-4e66-fab5-495995fd084e": "63d17e81a011a9746c94811b",
                            "1c865a6c-4668-420f-974e-e238acfc5a5d": "63ff8e895367c2261b4cb2ef",
                            "fb769d18-b846-4cc3-c7e4-93955dfc3d84": "603545f2dcda03378087e708",
                            "e2536b2c-a6fe-4d21-fb73-e68b46841344": "60354810e379f22e16560dbd",
                            "46509d68-7f9e-447f-eb76-de5a884cf3b0": "",
                            "fc7b149e-61be-4b34-a884-1234af9e98b0": "IHH1,IHH2,IHH3,IHH4,IHH5,MHH1,MHH2,MHH3,MHH4,MHH5",
                            "e838c579-15d3-43e7-dada-0f8345e15b21": "IAGMIN,IUTIL,ICONS,IMANU,IWHOLE,IRETAIL,ITRANS,IPROFSER,IREALE,IEDU,IHEALTH,IART,IACCO,MAGMIN,MUTIL,MCONS,MMANU,MWHOLE,MRETAIL,MTRANS,MPROFSER,MREALE,MEDU,MHEALTH,MART,MACCO",
                            "7c88cdbf-3801-4371-e709-50be083c7f75": "IAGMIN,IUTIL,ICONS,IMANU,IWHOLE,IRETAIL,ITRANS,IPROFSER,IREALE,IEDU,IHEALTH,IART,IACCO,MAGMIN,MUTIL,MCONS,MMANU,MWHOLE,MRETAIL,MTRANS,MPROFSER,MREALE,MEDU,MHEALTH,MART,MACCO,HS1I,HS2I,HS3I,HS1M,HS2M,HS3M",
                            "560c01da-6df8-4602-80b1-d321e4fac114": "63dc1f1362b9d001e6a1b485",
                            "d1451c74-4b6e-4cba-ef7f-defec6f1384d": "63dc1f1362b9d001e6a1b485",
                            "631955b9-06df-45d4-8136-b56c78193b22": "63dc1f1362b9d001e6a1b485",
                            "fa7e3420-a267-4196-d09b-5dca688a37ed": "arch_wind",
                            "157d4d89-7a8b-49d6-d5ce-bbdd97b1a401": "arch_wind",
                            "7e765d1a-a945-4008-d0d6-468c705b308a": "arch_wind",
                            "d4b8ddb0-fa3f-4f93-d48b-7b3993c07500": "max_state",
                            "590311bd-4ba7-414f-e249-7a3d5524bef0": "6303e51bd76c6d0e1f6be080",
                            "3be2570a-cb50-4c00-fcd7-9bad28979819": "62fef3a6cef2881193f2261d",
                            "17a98e75-4978-4ecf-8d5a-56ecdcc0e4e0": "62fefd688a30d30dac57bbd7",
                            "13b87f69-109f-452d-a0fe-4b4c10692950": "640200da475d895dfc2de1bd",
                            "3909cd82-5256-4925-9e10-a63d9adb865f": "1.0",
                            "c02f86bb-8c65-418f-e836-2ee1b8791a2d": "90.0",
                            "6cf56dec-68b9-4be9-e532-f9c422f7d57e": "60f5e2ae544e944c3cec0794",
                            "34fff30f-d199-4545-b7f6-138c4e5d0c24": "60f5e918544e944c3cec668b",
                            "9b2f055d-e708-42f5-bd92-c0479431e952": "incore:funcProbability",
                            "d923c37c-4b7e-41f1-e404-21003738d3c6": "incore:failureProbability",
                            "bb24e40b-03a4-48ca-f943-ffe72103a4cd": "incore:maxDamageState",
                            "e97632f0-ff75-4f82-fab5-1d9fccc07c33": "incore:maxDamageState",
                            "b2ada272-85f5-452a-f467-c5ef6ccd2262": "incore:popdislocationShp",
                            "30ef6df8-bdfe-4a36-f686-4157fdaf5fe8": "table",
                            "90b01539-1cb6-459b-abc9-a9d8fab0c664": "table",
                            "a644b3c8-8a01-4f49-ce10-827e48936ebf": "table",
                            "18d0b09b-b180-487b-fa2c-e7436edd8add": "table",
                            "0cfeaeb6-6a13-4eff-cf38-cbee21f56715": "shapefile",
                            "c528ca2d-f572-45b0-b038-2954415b4b09": "commresiliencegal",
                            "464e2963-c527-47ab-acfe-46e58727e99e": "commresiliencegal",
                            "d405acb0-b2dc-4f88-b806-e7c749897712": "commresiliencegal",
                            "e27dd10c-4d57-48e6-9a2e-6affeabf0c4d": "commresiliencegal",
                            "0f6c26c1-4d99-4e2b-bd36-12b1f6a22f9f": "commresiliencegal",
                            "09d53917-3618-4a91-99bc-8304a859a97e": "",
                            "5adea2be-db15-4aa8-c3ef-2b1432bb6267": "63e5af0262d82d2f5a1058ea",
                            "60757a49-6019-4ec7-cea4-f3f62aece949": "1", "bc73d0f5-e81e-40b6-acb7-c1670bdbf3a1": "",
                            "d283a461-3dd7-48bb-c272-d956d6f1fb9c": "641e1fccea308903b2b8c51a",
                            "9c1bc5cf-83c3-4be8-8d3f-96b4c9189a72": "641e1fff34810d74880b3985",
                            "d7726876-6dd9-4690-d141-b34e3b1e8f0a": "641e21a702414a24a5436dfe",
                            "a17d2606-cddd-4a1e-d218-bec8299cb94d": "641e2152ea308903b2b8c51c",
                            "4870c4dd-273b-4129-81a8-9f5a93145542": "641e209eea308903b2b8c51b",
                            "43d1286d-2731-4a37-bf7e-321fd56d5323": "641e20f134810d74880b3986"},
             "datasets": {"c484e0b1-dff2-412f-efe8-2e0e5321d667": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "97a3ce6f-5b5f-40c0-8a0c-e26ceb92635c": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "c9ab0651-864f-4b6b-c1c1-fc64d1f58de3": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "3f95a3fe-f1f7-4b4f-84af-30fe38d9c241": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "0e7373df-c450-4455-d10b-d16f5113f177": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "f12247ba-854d-4b8e-e081-c4441fd537cc": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "edf2d5e6-0ac3-4c73-add5-3e11552884c5": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "f8749e24-e188-4b27-838b-daa025e7a53c": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "b7c3e9d1-9697-4ebd-d79a-9daaf66b4fc1": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "6bb8a788-b553-42c0-93bc-56d76b907781": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "63a39c9d-9d9c-491c-ddba-ba7497ec0348": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "1fb15ca5-55db-4066-dbb6-a6f75d49aeb6": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "d92df4b0-48ba-46dd-9975-d04d90f82f2e": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "8460ca93-836c-4d48-f1e2-c9c031edca9c": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "0dff57fb-8f6c-4847-d00e-45a9d79dc8dc": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "f6806415-26e3-43bf-9585-62dc49080000": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "4208a3ee-2010-4f36-c8c4-4c90e7b11bfd": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "a201283a-e5bb-43ed-9f0f-06716ff1ef96": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "fd6039d6-3cc3-41f3-8de9-1836c579ad4a": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "6624d5c8-e7b8-42c4-aa0b-ea67b008912b": "42151f1b-a849-4b8e-bd6d-7a49c69e7642",
                          "eae9e675-44f8-4eb8-952b-415d41d31ecb": "42151f1b-a849-4b8e-bd6d-7a49c69e7642"}}

        )

        res = self.client.post(url, data=payload, headers=self.headers)

        # The code below is intended to delete test data, but there is no straightforward way to remove the test data
        # so I comment it out
        # if res.status_code == 200:
        #     index = 0
        #     is_space_ok = False
        #     while is_space_ok is False and index <= 5:
        #         time.sleep(5)
        #         id = res
        #         get_res = self.client.get(f"{url}{id}", headers=self.headers)
        #         index += 1
        #
        #         if get_res.status_code == 200:
        #             is_space_ok = True
        #             self.client.delete(f"{url}{id}", headers=self.headers)

