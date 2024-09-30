#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    source .env
else
    echo ".env file not found!"
    exit 1
fi

REALM="In-core"
GROUP="0unapproved"

# Get access token using credentials from .env file
TOKEN_RESPONSE=$(curl -s "${KEYCLOAK_URL}/auth/realms/master/protocol/openid-connect/token" \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "username=${KEYCLOAK_USERNAME}" \
    --data-urlencode "password=${KEYCLOAK_PASSWORD}" \
    --data-urlencode 'grant_type=password' \
    --data-urlencode 'client_id=admin-cli')

ACCESS_TOKEN=$(echo "${TOKEN_RESPONSE}" | jq -r .access_token)

# Check if the token was retrieved successfully
if [[ "${ACCESS_TOKEN}" == "null" || -z "${ACCESS_TOKEN}" ]]; then
    echo "Failed to retrieve access token. Please check your credentials or configuration."
    exit 1
fi

# Get group ID
GID=$(curl -s "${KEYCLOAK_URL}/auth/admin/realms/${REALM}/groups?search=${GROUP}" \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer ${ACCESS_TOKEN}" | jq -r '.[0].id')

# Capture raw user information
RAW_RESULT=$(curl -s "${KEYCLOAK_URL}/auth/admin/realms/${REALM}/groups/${GID}/members?max=9999" \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer ${ACCESS_TOKEN}")

# Clean up the access token (no need to store it in a file)
unset ACCESS_TOKEN

# Check if RAW_RESULT is a valid JSON array and contains users
if echo "${RAW_RESULT}" | jq empty 2>/dev/null; then
    if [ "$(echo "${RAW_RESULT}" | jq 'if type=="array" then length else 0 end')" -gt 0 ]; then
        # If users exist, extract user information
        RESULT=$(echo "${RAW_RESULT}" | jq -r '.[] | [.username, .firstName, .lastName, .email] | @csv')

        # Prepare email content
        EMAIL_BODY="Here is the list of members for the group ${GROUP}:\n\n${RESULT}"

        # Send the email
        echo -e "${EMAIL_BODY}" | mail -s "${EMAIL_SUBJECT}" "${EMAIL_RECIPIENT}"

        echo "Email sent to ${EMAIL_RECIPIENT}"
    else
        echo "No members found for the group ${GROUP}. No email sent."
    fi
else
    echo "Invalid response from Keycloak. Please check your connection or configuration."
fi

