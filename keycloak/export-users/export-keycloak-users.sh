#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: export-keycloak-users.sh [options]

Export Keycloak realm users to users.json, a CSV, and a plain-text list.

Options:
  --registered-within N     Only users whose account was created in the last N months.
  --registered-since DATE   Only users whose account was created on or after DATE
                            (YYYY-MM-DD, UTC). Mutually exclusive with
                            --registered-within.
  --active-within N         Only users with a LOGIN event in the last N months.
  --active-since DATE       Only users with a LOGIN event on or after DATE
                            (YYYY-MM-DD, UTC). Mutually exclusive with
                            --active-within.
                            Activity filters require user events to be enabled
                            on the realm; only logins within the realm's event
                            retention are visible.
  -o, --output FILE         CSV output path (default: users.csv).
                            The text list is written beside it with a .txt extension.
  -h, --help                Show this help.

Filters can be combined (a user must match all of them).

Environment:
  KEYCLOAK_ADMIN_PASS     Admin password for the master realm (required).
  KEYCLOAK_ADMIN_USER     Admin username (default: keycloak).
  KEYCLOAK_BASE           Server URL including /auth (default: https://tools.in-core.org/auth).
  KEYCLOAK_REALM          Realm to export (default: In-core).
  KEYCLOAK_GROUP          Optional group name (inc-core) or path (/parent/inc-core).
                          When set, only direct members of that group are exported.
                          Unset exports every user in the realm.

Examples:
  KEYCLOAK_ADMIN_PASS=... ./export-keycloak-users.sh
  KEYCLOAK_GROUP=inc-core KEYCLOAK_ADMIN_PASS=... ./export-keycloak-users.sh
  KEYCLOAK_ADMIN_PASS=... ./export-keycloak-users.sh --registered-within 3 -o new-users.csv
  KEYCLOAK_ADMIN_PASS=... ./export-keycloak-users.sh --registered-since 2026-01-01 -o new-users.csv
  KEYCLOAK_ADMIN_PASS=... ./export-keycloak-users.sh --active-within 6 -o active-users.csv
  KEYCLOAK_ADMIN_PASS=... ./export-keycloak-users.sh --active-since 2026-04-01 -o active-users.csv
EOF
}

KEYCLOAK_BASE="${KEYCLOAK_BASE:-https://tools.in-core.org/auth}"
REALM="${KEYCLOAK_REALM:-In-core}"
ADMIN_REALM="master"
ADMIN_USER="${KEYCLOAK_ADMIN_USER:-keycloak}"
GROUP_FILTER="${KEYCLOAK_GROUP:-}"
CLIENT_ID="admin-cli"

REGISTERED_WITHIN=""
REGISTERED_SINCE=""
ACTIVE_WITHIN=""
ACTIVE_SINCE=""
CSV_OUT="users.csv"
JSON_OUT="users.json"

require_months() {
  if [[ ! "${2:-}" =~ ^[1-9][0-9]*$ ]]; then
    echo "$1 requires a positive integer number of months" >&2
    exit 1
  fi
}

require_date() {
  local flag="$1" value="${2:-}"
  if [[ ! "$value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "$flag requires a date as YYYY-MM-DD" >&2
    exit 1
  fi
  # Reject invalid calendar dates (BSD date on macOS, GNU date on Linux).
  if ! date -u -j -f "%Y-%m-%d" "$value" +%Y-%m-%d >/dev/null 2>&1 \
     && ! date -u -d "$value" +%Y-%m-%d >/dev/null 2>&1; then
    echo "$flag: invalid date '$value'" >&2
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registered-within) require_months "$1" "${2:-}"; REGISTERED_WITHIN="$2"; shift 2 ;;
    --registered-since)  require_date "$1" "${2:-}"; REGISTERED_SINCE="$2"; shift 2 ;;
    --active-within)     require_months "$1" "${2:-}"; ACTIVE_WITHIN="$2"; shift 2 ;;
    --active-since)      require_date "$1" "${2:-}"; ACTIVE_SINCE="$2"; shift 2 ;;
    -o|--output)         CSV_OUT="${2:?$1 requires a file path}"; shift 2 ;;
    -h|--help)           usage; exit 0 ;;
    *)                   echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -n "$REGISTERED_WITHIN" && -n "$REGISTERED_SINCE" ]]; then
  echo "Use only one of --registered-within or --registered-since" >&2
  exit 1
fi
if [[ -n "$ACTIVE_WITHIN" && -n "$ACTIVE_SINCE" ]]; then
  echo "Use only one of --active-within or --active-since" >&2
  exit 1
fi

ADMIN_PASS="${KEYCLOAK_ADMIN_PASS:?Set KEYCLOAK_ADMIN_PASS env var}"

# Epoch seconds N calendar months ago (BSD date on macOS, GNU date on Linux).
months_ago_epoch() {
  date -u -v-"$1"m +%s 2>/dev/null || date -u -d "$1 months ago" +%s
}

# Epoch seconds at 00:00:00 UTC on YYYY-MM-DD.
date_to_epoch() {
  date -u -j -f "%Y-%m-%d" "$1" +%s 2>/dev/null || date -u -d "$1" +%s
}

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

TOKEN=""
fetch_token() {
  local resp body code
  resp=$(curl -sS -w "\n%{http_code}" -X POST \
    "$KEYCLOAK_BASE/realms/$ADMIN_REALM/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=password" \
    -d "client_id=$CLIENT_ID" \
    -d "username=$ADMIN_USER" \
    --data-urlencode "password=$ADMIN_PASS")

  body=$(echo "$resp" | sed '$d')
  code=$(echo "$resp" | tail -n1)

  if [[ "$code" != "200" ]]; then
    echo "Token request failed ($code): $body" >&2
    exit 1
  fi

  TOKEN=$(echo "$body" | jq -r '.access_token // empty')
  if [[ -z "$TOKEN" ]]; then
    echo "No access_token in token response: $body" >&2
    exit 1
  fi
}

# GET an admin API path into $ADMIN_BODY. Not meant to be called in a
# subshell: admin tokens are short-lived (60s by default), and a 401 refreshes
# the global $TOKEN before retrying once.
ADMIN_BODY=""
admin_get() {
  local path="$1" attempt resp code
  for attempt in 1 2; do
    resp=$(curl -sS -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" \
      "$KEYCLOAK_BASE/admin/realms/$REALM/$path")
    ADMIN_BODY=$(echo "$resp" | sed '$d')
    code=$(echo "$resp" | tail -n1)

    if [[ "$code" == "401" && "$attempt" == "1" ]]; then
      fetch_token
      continue
    fi
    if [[ "$code" != "200" ]]; then
      echo "Request failed ($code) for $path: $ADMIN_BODY" >&2
      exit 1
    fi
    return
  done
}

# Page through an admin API list endpoint, writing one JSON array per page
# into $2 (a directory). $1 is the path including its query string.
fetch_all_pages() {
  local path="$1" out_dir="$2" first=0 page=200 body count
  mkdir -p "$out_dir"
  while : ; do
    admin_get "${path}&first=$first&max=$page"
    body="$ADMIN_BODY"

    if [[ "$(echo "$body" | jq -r 'type')" != "array" ]]; then
      echo "Unexpected response (not array) for $path: $body" >&2
      exit 1
    fi

    count=$(echo "$body" | jq 'length')
    [[ "$count" -eq 0 ]] && break

    echo "$body" > "$out_dir/$(printf '%08d' "$first").json"
    first=$((first + page))
  done
}

fetch_token

# Resolve activity cutoff (epoch seconds) and YYYY-MM-DD for the events API.
ACTIVE_CUTOFF=""
DATE_FROM=""
if [[ -n "$ACTIVE_WITHIN" ]]; then
  ACTIVE_CUTOFF=$(months_ago_epoch "$ACTIVE_WITHIN")
  DATE_FROM=$(jq -nr --argjson t "$ACTIVE_CUTOFF" '$t | strftime("%Y-%m-%d")')
elif [[ -n "$ACTIVE_SINCE" ]]; then
  ACTIVE_CUTOFF=$(date_to_epoch "$ACTIVE_SINCE")
  DATE_FROM="$ACTIVE_SINCE"
fi

# 1) optional: last LOGIN time per user from realm events
LOGINS_FILE="$WORK_DIR/logins.json"
echo "{}" > "$LOGINS_FILE"

if [[ -n "$ACTIVE_CUTOFF" ]]; then
  admin_get "events/config"
  EVENTS_CONFIG="$ADMIN_BODY"
  if [[ "$(echo "$EVENTS_CONFIG" | jq -r '.eventsEnabled')" != "true" ]]; then
    cat >&2 <<EOF
User events are disabled on realm '$REALM', so login history is unavailable.
Enable them in the admin console (Realm settings > Events > User events settings),
then logins from that point on can be queried with --active-within / --active-since.
EOF
    exit 1
  fi

  ENABLED_TYPES=$(echo "$EVENTS_CONFIG" | jq -r '.enabledEventTypes // [] | join(",")')
  if [[ -n "$ENABLED_TYPES" && ",$ENABLED_TYPES," != *",LOGIN,"* ]]; then
    echo "LOGIN is not in the realm's saved event types ($ENABLED_TYPES); cannot determine activity." >&2
    exit 1
  fi

  EXPIRATION=$(echo "$EVENTS_CONFIG" | jq -r '.eventsExpiration // 0')
  WINDOW_SECONDS=$(( $(date -u +%s) - ACTIVE_CUTOFF ))
  if [[ "$EXPIRATION" -gt 0 && "$EXPIRATION" -lt "$WINDOW_SECONDS" ]]; then
    if [[ -n "$ACTIVE_WITHIN" ]]; then
      echo "Warning: events expire after $((EXPIRATION / 86400)) days, so only logins" \
        "from that period are included (requested $ACTIVE_WITHIN months)." >&2
    else
      echo "Warning: events expire after $((EXPIRATION / 86400)) days, so only logins" \
        "from that period are included (requested since $ACTIVE_SINCE)." >&2
    fi
  fi

  fetch_all_pages "events?type=LOGIN&dateFrom=$DATE_FROM" "$WORK_DIR/events"
  if compgen -G "$WORK_DIR/events/*.json" > /dev/null; then
    jq -s '
      add
      | map(select(.userId != null))
      | group_by(.userId)
      | map({ key: .[0].userId, value: (map(.time) | max) })
      | from_entries
    ' "$WORK_DIR"/events/*.json > "$LOGINS_FILE"
  fi
  echo "Found $(jq 'length' "$LOGINS_FILE") users with logins since $DATE_FROM"
fi

# 2) users. KEYCLOAK_GROUP limits the export to direct members of one group.
USER_PATH="users?briefRepresentation=false"
if [[ -n "$GROUP_FILTER" ]]; then
  if [[ "$GROUP_FILTER" == /* ]]; then
    GROUP_SEARCH="${GROUP_FILTER##*/}"
  else
    GROUP_SEARCH="$GROUP_FILTER"
  fi
  GROUP_SEARCH_ENC=$(jq -nr --arg s "$GROUP_SEARCH" '$s | @uri')
  fetch_all_pages "groups?exact=true&search=$GROUP_SEARCH_ENC" "$WORK_DIR/groups"

  if compgen -G "$WORK_DIR/groups/*.json" > /dev/null; then
    jq -s 'add // []' "$WORK_DIR"/groups/*.json > "$WORK_DIR/groups.json"
  else
    echo "[]" > "$WORK_DIR/groups.json"
  fi

  if [[ "$GROUP_FILTER" == /* ]]; then
    jq --arg p "$GROUP_FILTER" '[.[] | select(.path == $p)]' \
      "$WORK_DIR/groups.json" > "$WORK_DIR/group-matches.json"
  else
    jq --arg n "$GROUP_FILTER" '[.[] | select(.name == $n)]' \
      "$WORK_DIR/groups.json" > "$WORK_DIR/group-matches.json"
  fi

  MATCH_COUNT=$(jq 'length' "$WORK_DIR/group-matches.json")
  if [[ "$MATCH_COUNT" -eq 0 ]]; then
    echo "No Keycloak group matching '$GROUP_FILTER' in realm '$REALM'." >&2
    exit 1
  fi
  if [[ "$MATCH_COUNT" -gt 1 ]]; then
    echo "Multiple groups match '$GROUP_FILTER'. Set KEYCLOAK_GROUP to one of these paths:" >&2
    jq -r '.[].path' "$WORK_DIR/group-matches.json" >&2
    exit 1
  fi

  GROUP_ID=$(jq -r '.[0].id' "$WORK_DIR/group-matches.json")
  GROUP_PATH=$(jq -r '.[0].path' "$WORK_DIR/group-matches.json")
  echo "Filtering to direct members of $GROUP_PATH"
  USER_PATH="groups/$GROUP_ID/members?briefRepresentation=false"
fi

fetch_all_pages "$USER_PATH" "$WORK_DIR/users"
jq -s 'add // []' "$WORK_DIR"/users/*.json > "$JSON_OUT" 2>/dev/null || echo "[]" > "$JSON_OUT"
echo "Wrote $JSON_OUT (total: $(jq 'length' "$JSON_OUT"))"

REGISTERED_CUTOFF_MS=0
if [[ -n "$REGISTERED_WITHIN" ]]; then
  REGISTERED_CUTOFF_MS=$(( $(months_ago_epoch "$REGISTERED_WITHIN") * 1000 ))
elif [[ -n "$REGISTERED_SINCE" ]]; then
  REGISTERED_CUTOFF_MS=$(( $(date_to_epoch "$REGISTERED_SINCE") * 1000 ))
fi

# 3) CSV. Header must start with "emailAddress" (unquoted) for the webtool import.
{
  echo "emailAddress,id,username,firstName,lastName,enabled,createdAt,lastLogin"
  jq -r \
    --argjson regCutoff "$REGISTERED_CUTOFF_MS" \
    --argjson activeFilter "$([[ -n "$ACTIVE_CUTOFF" ]] && echo true || echo false)" \
    --slurpfile logins "$LOGINS_FILE" '
    def iso: if . == null then "" else (. / 1000 | floor | todate) end;
    $logins[0] as $last
    | .[]
    | select((.email // "") != "")
    | select((.createdTimestamp // 0) >= $regCutoff)
    | select(($activeFilter | not) or ($last[.id] != null))
    | [ .email, .id, .username, .firstName, .lastName, .enabled,
        (.createdTimestamp | iso), ($last[.id] | iso) ]
    | @csv
  ' "$JSON_OUT"
} > "$CSV_OUT"

echo "Wrote $CSV_OUT (total: $(($(wc -l < "$CSV_OUT") - 1)))"

# 4) Plain text: one "email First Last" line per CSV row.
TXT_OUT="${CSV_OUT%.*}.txt"
[[ "$TXT_OUT" == "$CSV_OUT" ]] && TXT_OUT="${CSV_OUT}.txt"
jq -r \
  --argjson regCutoff "$REGISTERED_CUTOFF_MS" \
  --argjson activeFilter "$([[ -n "$ACTIVE_CUTOFF" ]] && echo true || echo false)" \
  --slurpfile logins "$LOGINS_FILE" '
  $logins[0] as $last
  | .[]
  | select((.email // "") != "")
  | select((.createdTimestamp // 0) >= $regCutoff)
  | select(($activeFilter | not) or ($last[.id] != null))
  | . as $u
  | [($u.firstName // ""), ($u.lastName // "")]
  | map(gsub("^\\s+|\\s+$"; ""))
  | map(select(. != ""))
  | join(" ") as $name
  | if $name == "" then $u.email else "\($u.email) \($name)" end
' "$JSON_OUT" > "$TXT_OUT"

echo "Wrote $TXT_OUT (total: $(wc -l < "$TXT_OUT" | tr -d " "))"
