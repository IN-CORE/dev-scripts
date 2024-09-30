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
curl -s "${KEYCLOAK_URL}/auth/realms/master/protocol/openid-connect/token" \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "username=${KEYCLOAK_USERNAME}" \
    --data-urlencode "password=${KEYCLOAK_PASSWORD}" \
    --data-urlencode 'grant_type=password' \
    --data-urlencode 'client_id=admin-cli' | jq -r .access_token > /tmp/access_token

# Get group ID
GID=$(curl -s "${KEYCLOAK_URL}/auth/admin/realms/${REALM}/groups?search=${GROUP}" \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $(cat /tmp/access_token)" | jq -r '.[0].id')

# Output user information
echo "username,firstName,lastName,email"
curl -s "${KEYCLOAK_URL}/auth/admin/realms/${REALM}/groups/${GID}/members?max=9999" \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer $(cat /tmp/access_token)" | jq -r '.[] | [.username, .firstName, .lastName, .email] | @csv'

# Clean up
rm /tmp/access_token
