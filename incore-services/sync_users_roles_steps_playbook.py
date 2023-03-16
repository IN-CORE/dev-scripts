import json
import requests
import os

def create_roles(base_url, headers):
    """
    create roles for each testbed
    :param base_url:
    :return:
    """
    querystrings = [
        {
            "name": "leader",
            "description": "community%20leader"
        },
        {
            "name": "member",
            "description": "community%20member"
        },
    ]

    for qs in querystrings:
        response = requests.request("POST", base_url + "/roles", headers=headers, params=qs)
        print(response.text)


def create_steps(base_url, headers):
    """
    prepaopulate steps and their status
    :param base_url:
    :return:
    """
    querystrings = [
        {"step_id": "1", "substep_id": "1", "status": "pending"},
        {"step_id": "1", "substep_id": "2", "status": "pending"},
        {"step_id": "1", "substep_id": "3", "status": "pending"},
        {"step_id": "1", "substep_id": "4", "status": "pending"},

        {"step_id": "2", "substep_id": "1", "status": "pending"},
        {"step_id": "2", "substep_id": "2", "status": "pending"},
        {"step_id": "2", "substep_id": "3", "status": "pending"},
        {"step_id": "2", "substep_id": "4", "status": "pending"},
        {"step_id": "2", "substep_id": "5", "status": "pending"},

        {"step_id": "3", "substep_id": "1", "status": "pending"},
        {"step_id": "3", "substep_id": "2", "status": "pending"},
        {"step_id": "3", "substep_id": "3", "status": "pending"},
        {"step_id": "3", "substep_id": "4", "status": "pending"},
        {"step_id": "3", "substep_id": "5", "status": "pending"},

        {"step_id": "4", "substep_id": "1", "status": "pending"},
        {"step_id": "4", "substep_id": "2", "status": "pending"},
        {"step_id": "4", "substep_id": "3", "status": "pending"},

        {"step_id": "5", "substep_id": "1", "status": "pending"},
        {"step_id": "5", "substep_id": "2", "status": "pending"},
        {"step_id": "5", "substep_id": "3", "status": "pending"},

        {"step_id": "6", "substep_id": "1", "status": "pending"},
        {"step_id": "6", "substep_id": "2", "status": "pending"},
        {"step_id": "6", "substep_id": "3", "status": "pending"},
    ]

    for qs in querystrings:
        response = requests.request("POST", base_url + "/steps", headers=headers, params=qs)
        print(response.text)


def create_user(base_url, headers, userinfo_list):
    """
    post to maestro service
    :param base_url:
    :param userinfo_list:
    :return:
    """
    for userinfo in userinfo_list:

        payload = json.dumps(userinfo)
        response = requests.request("POST", base_url + "/users", data=payload, headers=headers)
        print(response.text)


def get_userinfo_from_keycloak(username_list, keycloak_base_url, admin_username, admin_password, realm="In-core"):
    """
    given list of usernames get their userinfo from keycloak?
    :param username_list:
    :param keycloak_url:
    :return:
    """

    token_url = keycloak_base_url + "/realms/master/protocol/openid-connect/token"
    payload = "client_id=admin-cli&grant_type=password&username={0}&password={1}".format(admin_username, admin_password)
    token_response = requests.request("POST", token_url, data=payload, headers={
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    })
    token = token_response.json()["access_token"]

    userinfo_url = keycloak_base_url + "/admin/realms/{0}/users?exact=true".format(realm)
    userinfo_list = []
    for username in username_list:
        querystring = {"username": username}
        response = requests.request("GET", userinfo_url, headers={
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Authorization': "bearer " + token
        }, params=querystring)

        userinfo_list.extend(response.json())

    return userinfo_list


def get_userinfo_from_keycloak_group(group_id, keycloak_base_url, admin_username, admin_password, realm="In-core"):
    """
    given list of usernames get their userinfo from keycloak?
    :param group_id:
    :param keycloak_url:
    :return:
    """

    token_url = keycloak_base_url + "/realms/master/protocol/openid-connect/token"
    payload = "client_id=admin-cli&grant_type=password&username={0}&password={1}".format(admin_username, admin_password)
    token_response = requests.request("POST", token_url, data=payload, headers={
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    })
    token = token_response.json()["access_token"]

    userinfo_url = keycloak_base_url + "/admin/realms/{0}/groups/{1}/members".format(realm, group_id)
    response = requests.request("GET", userinfo_url, headers={
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Authorization': "bearer " + token
    })

    return response.json()


# attach roles
def assign_roles(base_url):
    pass


if __name__ == "__main__":
    realm = os.getenv("REALM")
    auth_token = os.getenv("AUTH_TOKEN")
    server_base_url = os.getenv("SERVER_BASE_URL")
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    headers = {
        'Authorization': auth_token,
        'Content-Type': "application/json",
        'cache-control': "no-cache"
    }
    keycloak_base_url = server_base_url + "/auth"

    config = [
        {
            "testbed": "slc",
            "url": server_base_url + "/maestro/slc",
            "group_name": "incore_slc_user",
            "group_id": os.getenv("SLC_GROUP_ID")  # get this information from keycloak
        },
        {
            "testbed": "galveston",
            "url": server_base_url + "/maestro/galveston",
            "group_name": "incore_galveston_user",
            "group_id":  os.getenv("JOPLIN_GROUP_ID")
        },
        {
            "testbed": "joplin",
            "url": server_base_url + "/maestro/joplin",
            "group_name": "incore_joplin_user",
            "group_id": os.getenv("GALVESTON_GROUP_ID")  # get this information from keycloak
        },
    ]

    for item in config:
        userinfo_list = get_userinfo_from_keycloak_group(item["group_id"], keycloak_base_url, admin_username,
                                                         admin_password,realm=realm)
        create_user(item["url"], headers, userinfo_list)

        create_roles(item["url"], headers)
        create_steps(item["url"], headers)


