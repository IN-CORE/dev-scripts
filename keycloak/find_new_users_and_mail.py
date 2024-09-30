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
   SMTP_USER: Your University of Illinois email (for SMTP authentication).
   SMTP_PASS: The password for your University of Illinois email.
   EMAIL_FROM: The "From" email address.

2. Run the Script:
   python3 keycloak_email_report.py

3. Usage in Kubernetes CronJob:
   The script can be mounted and run in a Kubernetes CronJob that executes
   periodically (e.g., every 15 minutes). The script is designed to be flexible
   and can be scheduled to run at your desired interval.

=============================================================
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
keycloak_url = os.getenv("KEYCLOAK_URL")
username = os.getenv("KEYCLOAK_USERNAME")
password = os.getenv("KEYCLOAK_PASSWORD")
realm = os.getenv("REALM", "In-core")
group = os.getenv("GROUP", "0unapproved")
email_recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
email_subject = os.getenv("EMAIL_SUBJECT", "Keycloak Group Members Report")
email_from = os.getenv("EMAIL_FROM", "your_netid@illinois.edu")
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")

def get_keycloak_token():
    """Get access token from Keycloak."""
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
    else:
        raise Exception(f"Failed to get access token: {response.text}")


def get_group_id(token):
    """Get group ID from Keycloak based on group name."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    group_url = f"{keycloak_url}/auth/admin/realms/{realm}/groups?search={group}"
    response = requests.get(group_url, headers=headers)

    if response.status_code == 200:
        group_data = response.json()
        if group_data:
            return group_data[0]['id']
        else:
            raise Exception(f"Group {group} not found.")
    else:
        raise Exception(f"Failed to fetch group ID: {response.text}")


def get_group_members(token, group_id):
    """Get members of the group from Keycloak."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    members_url = f"{keycloak_url}/auth/admin/realms/{realm}/groups/{group_id}/members?max=9999"
    response = requests.get(members_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch group members: {response.text}")


def send_email(body):
    """Send an email with the provided content."""
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = ", ".join(email_recipients)
    msg['Subject'] = email_subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('outbound-relays.techservices.illinois.edu', 25)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(email_from, email_recipients, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")


def main():
    try:
        # Step 1: Get Keycloak access token
        token = get_keycloak_token()

        # Step 2: Get group ID
        group_id = get_group_id(token)

        # Step 3: Get group members
        members = get_group_members(token, group_id)

        if members:
            # Prepare the CSV content
            user_info = "username,firstName,lastName,email\n"
            user_info += "\n".join([
                f"{member['username']},{member.get('firstName', '')},{member.get('lastName', '')},{member.get('email', '')}"
                for member in members
            ])

            # Step 4: Send email with the user info
            send_email(user_info)
        else:
            print(f"No members found for group: {group}.")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
