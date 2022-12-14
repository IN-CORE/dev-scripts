import json
import requests


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


def get_userinfo_from_keycloak(username_list, keycloak_base_url, admin_username, admin_password):
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

    userinfo_url = keycloak_base_url + "/admin/realms/In-core/users?exact=true"
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


def get_userinfo_from_keycloak_group(group_id, keycloak_base_url, admin_username, admin_password):
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

    userinfo_url = keycloak_base_url + "/admin/realms/In-core/groups/{0}/members".format(group_id)
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
    auth_token = ""
    headers = {
        'Authorization': auth_token,
        'Content-Type': "application/json",
        'cache-control': "no-cache"
    }

    keycloak_base_url = "https://incore-dev.ncsa.illinois.edu/auth"
    admin_username = ""
    admin_password = ""

    config = [
        {
            "testbed": "slc",
            "url": "https://incore-dev.ncsa.illinois.edu/maestro/slc",
            "group_name": "incore_slc_user",
            "group_id": "18ec08f4-86ae-4ec3-bb57-54c19e5398cf"  # get this information from keycloak
        },
        {
            "testbed": "galveston",
            "url": "https://incore-dev.ncsa.illinois.edu/maestro/galveston",
            "group_name": "incore_galveston_user",
            "group_id": "c098e80e-64a0-43b0-91b2-66a79dadb225"  # get this informatio from keycloak
        },
        {
            "testbed": "joplin",
            "url": "https://incore-dev.ncsa.illinois.edu/maestro/joplin",
            "group_name": "incore_joplin_user",
            "group_id": "2b691eaf-22ff-41ea-b8f5-d835a4a9e35a"  # get this informatio from keycloak
        },
    ]

    for item in config:

        create_roles(item["url"], headers)
        create_steps(item["url"], headers)

        userinfo_list = get_userinfo_from_keycloa_group(item["group_id"],
                                                        keycloak_base_url,
                                                        admin_username,
                                                        admin_password)
        create_user(item["url"], headers, userinfo_list)
