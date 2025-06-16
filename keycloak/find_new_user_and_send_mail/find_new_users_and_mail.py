#!/usr/bin/env python3

"""
=============================================================
Script: keycloak_email_report.py
Description: This Python script retrieves user information from
a Keycloak group and sends the results via email. It authenticates
with Keycloak, queries a specified group for its members, and sends
the list of users in CSV format to the provided email recipients.

How to Use:
1. Environment Variables:
   The Python script retrieves configuration values from environment
   variables. You must ensure that these variables are correctly set:

   KEYCLOAK_URL: The base URL of your Keycloak server.
   KEYCLOAK_USERNAME: Your Keycloak admin username.
   KEYCLOAK_PASSWORD: Your Keycloak admin password.
   REALM: The Keycloak realm where your group resides.
   GROUP: The group name you want to query.

   EMAIL_RECIPIENTS: A comma-separated list of email recipients.
   EMAIL_SUBJECT: The subject of the email.
   EMAIL_BODY: The body of the email (user report content).
   EMAIL_FROM: The "From" email address.

2. Run the Script:
   python3 keycloak_email_report.py

3. Usage in Kubernetes CronJob:
   The script can be mounted and run in a Kubernetes CronJob that executes
   periodically (e.g., every 15 minutes). The script is designed to be flexible
   and can be scheduled to run at your desired interval.

=============================================================
"""

#!/usr/bin/env python3

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

load_dotenv()

keycloak_url = os.getenv("KEYCLOAK_URL")
username = os.getenv("KEYCLOAK_USERNAME")
password = os.getenv("KEYCLOAK_PASSWORD")
realm = os.getenv("REALM", "In-core")
group = os.getenv("GROUP", "0unapproved")
email_recipients = os.getenv("EMAIL_RECIPIENTS").split(",")
email_subject = os.getenv("EMAIL_SUBJECT")
email_body = os.getenv("EMAIL_BODY")
email_from = os.getenv("EMAIL_FROM")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))

def get_keycloak_token():
    token_url = f"{keycloak_url}/auth/realms/master/protocol/openid-connect/token"
    data = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": "admin-cli"
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    raise Exception(f"Failed to get access token: {response.text}")

def get_group_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    group_url = f"{keycloak_url}/auth/admin/realms/{realm}/groups?search={group}"
    response = requests.get(group_url, headers=headers)
    if response.status_code == 200:
        group_data = response.json()
        return group_data[0]['id'] if group_data else None
    raise Exception(f"Failed to fetch group ID: {response.text}")

def get_group_members(token, group_id):
    headers = {"Authorization": f"Bearer {token}"}
    members_url = f"{keycloak_url}/auth/admin/realms/{realm}/groups/{group_id}/members?max=9999"
    response = requests.get(members_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to fetch group members: {response.text}")

def send_email(body):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = ", ".join(email_recipients)
    msg['Subject'] = email_subject
    msg.attach(MIMEText(body, 'plain'))
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.sendmail(email_from, email_recipients, msg.as_string())
        print("Email sent successfully.")

def main():
    try:
        token = get_keycloak_token()
        group_id = get_group_id(token)
        if group_id:
            members = get_group_members(token, group_id)
            if members:
                user_info = "username,firstName,lastName,email\n"
                user_info += "\n".join([f"{m['username']},{m.get('firstName', '')},{m.get('lastName', '')},{m.get('email', '')}" for m in members])
                send_email(user_info)
            else:
                print(f"No members found in group: {group}. No email sent.")
        else:
            print(f"Group {group} not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

