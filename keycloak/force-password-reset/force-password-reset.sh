#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: force-password-reset.sh (--user NAME ... | --users-file FILE | --all) [options]

Make Keycloak users set a new password: add the UPDATE_PASSWORD required
action (or, with --random-password, replace the password with a random one),
then sign out their sessions. Dry run by default: nothing changes until you
pass --apply.

Targets (pick one kind):
  -u, --user NAME           Username (exact match). Repeat for several users.
  -f, --users-file FILE     File with one username per line (blank lines and
                            lines starting with # are ignored).
  --all                     Every user in the realm.

Options:
  -x, --exclude NAME        Username to skip. Repeatable. Use for service and
                            test accounts (e.g. maestro, incrtest).
  --exclude-file FILE       File of usernames to skip (same format as --users-file).
  --include-no-password     Also flag users with no stored password (e.g. users
                            who only sign in through an identity provider).
                            Skipped by default, since they have nothing to rotate.
  --no-logout               Don't sign users out. By default every targeted
                            user's sessions are ended, so they hit the password
                            change now instead of when their tokens expire.
  --random-password         Also replace each user's password with a random one
                            that nobody sees, so an old (possibly leaked)
                            password stops working. Users then get back in only
                            through "Forgot password", so the realm must have
                            reset-password enabled and SMTP configured; the
                            script checks both and stops if either is missing.
  --apply                   Make the changes. Without it, only report.
  -h, --help                Show this help.

Always skipped: service-account-* users (client service accounts) and
disabled users.

Environment:
  KEYCLOAK_ADMIN_PASS     Admin password for the master realm (required).
  KEYCLOAK_ADMIN_USER     Admin username (default: keycloak).
  KEYCLOAK_BASE           Server URL including /auth (default: https://tools.in-core.org/auth).
  KEYCLOAK_REALM          Realm (default: In-core).

Examples:
  # dry run on two developers
  KEYCLOAK_ADMIN_PASS=... ./force-password-reset.sh -u alice -u bob
  # apply to them (required action + sign-out)
  KEYCLOAK_ADMIN_PASS=... ./force-password-reset.sh -u alice -u bob --apply
  # same, but also scramble their passwords
  KEYCLOAK_ADMIN_PASS=... ./force-password-reset.sh -u alice -u bob --random-password --apply
  # dev cluster, everyone except service/test accounts
  KEYCLOAK_BASE=https://dev.in-core.org/auth KEYCLOAK_ADMIN_PASS=... \
    ./force-password-reset.sh --all -x maestro -x incrtest --apply
EOF
}

KEYCLOAK_BASE="${KEYCLOAK_BASE:-https://tools.in-core.org/auth}"
REALM="${KEYCLOAK_REALM:-In-core}"
ADMIN_REALM="master"
ADMIN_USER="${KEYCLOAK_ADMIN_USER:-keycloak}"
CLIENT_ID="admin-cli"
ACTION="UPDATE_PASSWORD"

USERS=()
EXCLUDES=()
ALL=false
APPLY=false
LOGOUT=true
INCLUDE_NO_PASSWORD=false
RANDOM_PASSWORD=false

read_name_file() {
  local file="$1" line
  [[ -r "$file" ]] || { echo "Cannot read $file" >&2; exit 1; }
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="$(echo "$line" | tr -d '[:space:]')"
    [[ -n "$line" ]] && echo "$line"
  done < "$file"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--user)             USERS+=("${2:?$1 requires a username}"); shift 2 ;;
    -f|--users-file)       while IFS= read -r n; do USERS+=("$n"); done < <(read_name_file "${2:?$1 requires a file}"); shift 2 ;;
    --all)                 ALL=true; shift ;;
    -x|--exclude)          EXCLUDES+=("${2:?$1 requires a username}"); shift 2 ;;
    --exclude-file)        while IFS= read -r n; do EXCLUDES+=("$n"); done < <(read_name_file "${2:?$1 requires a file}"); shift 2 ;;
    --include-no-password) INCLUDE_NO_PASSWORD=true; shift ;;
    --no-logout)           LOGOUT=false; shift ;;
    --random-password)     RANDOM_PASSWORD=true; shift ;;
    --apply)               APPLY=true; shift ;;
    -h|--help)             usage; exit 0 ;;
    *)                     echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ "$ALL" == true && ${#USERS[@]} -gt 0 ]]; then
  echo "Use either --all or --user/--users-file, not both" >&2
  exit 1
fi
if [[ "$ALL" == false && ${#USERS[@]} -eq 0 ]]; then
  echo "Pick targets: --user NAME, --users-file FILE, or --all" >&2
  usage >&2
  exit 1
fi

ADMIN_PASS="${KEYCLOAK_ADMIN_PASS:?Set KEYCLOAK_ADMIN_PASS env var}"

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
    --data-urlencode "username=$ADMIN_USER" \
    --data-urlencode "password=$ADMIN_PASS")
  body=$(echo "$resp" | sed '$d')
  code=$(echo "$resp" | tail -n1)
  if [[ "$code" != "200" ]]; then
    echo "Token request failed ($code): $body" >&2
    exit 1
  fi
  TOKEN=$(echo "$body" | jq -r '.access_token // empty')
  [[ -n "$TOKEN" ]] || { echo "No access_token in token response" >&2; exit 1; }
}

# admin_call METHOD PATH [JSON_BODY] -> sets $ADMIN_BODY and $ADMIN_CODE.
# PATH is relative to the realm ("" for the realm itself). The body goes to
# curl on stdin, so it never shows up in the process list.
# Admin tokens are short-lived; a 401 refreshes $TOKEN and retries once.
# Not meant to be called in a subshell.
ADMIN_BODY=""
ADMIN_CODE=""
admin_call() {
  local method="$1" path="$2" data="${3:-}" attempt resp
  local url="$KEYCLOAK_BASE/admin/realms/$REALM${path:+/$path}"
  for attempt in 1 2; do
    if [[ -n "$data" ]]; then
      resp=$(printf '%s' "$data" | curl -sS -w "\n%{http_code}" -X "$method" \
        -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
        --data-binary @- "$url")
    else
      resp=$(curl -sS -w "\n%{http_code}" -X "$method" \
        -H "Authorization: Bearer $TOKEN" "$url")
    fi
    ADMIN_BODY=$(echo "$resp" | sed '$d')
    ADMIN_CODE=$(echo "$resp" | tail -n1)
    if [[ "$ADMIN_CODE" == "401" && "$attempt" == "1" ]]; then
      fetch_token
      continue
    fi
    return
  done
}

admin_get_ok() {
  admin_call GET "$1"
  if [[ "$ADMIN_CODE" != "200" ]]; then
    echo "Request failed ($ADMIN_CODE) for $1: $ADMIN_BODY" >&2
    exit 1
  fi
}

fetch_token

if [[ "$RANDOM_PASSWORD" == true ]]; then
  command -v openssl > /dev/null || { echo "--random-password needs openssl" >&2; exit 1; }
  admin_get_ok ""
  problems=()
  [[ "$(echo "$ADMIN_BODY" | jq -r '.resetPasswordAllowed')" == "true" ]] \
    || problems+=("'Forgot password' is off (Realm settings > Login > Forgot password)")
  [[ -n "$(echo "$ADMIN_BODY" | jq -r '.smtpServer.host // empty')" ]] \
    || problems+=("no SMTP server (Realm settings > Email)")
  if [[ ${#problems[@]} -gt 0 ]]; then
    echo "--random-password would lock users out with no way back in:" >&2
    printf '  - %s\n' "${problems[@]}" >&2
    exit 1
  fi
fi

random_password() {
  openssl rand -base64 36 | tr -d '\n'
}

# Collect target users (full representations) into $WORK_DIR/users.json.
if [[ "$ALL" == true ]]; then
  first=0; page=200
  mkdir -p "$WORK_DIR/pages"
  while : ; do
    admin_get_ok "users?briefRepresentation=false&first=$first&max=$page"
    count=$(echo "$ADMIN_BODY" | jq 'length')
    [[ "$count" -eq 0 ]] && break
    echo "$ADMIN_BODY" > "$WORK_DIR/pages/$(printf '%08d' "$first").json"
    first=$((first + page))
  done
  if compgen -G "$WORK_DIR/pages/*.json" > /dev/null; then
    jq -s 'add' "$WORK_DIR"/pages/*.json > "$WORK_DIR/users.json"
  else
    echo "[]" > "$WORK_DIR/users.json"
  fi
else
  echo "[]" > "$WORK_DIR/users.json"
  for name in "${USERS[@]}"; do
    enc=$(jq -nr --arg s "$name" '$s | @uri')
    admin_get_ok "users?username=$enc&exact=true&briefRepresentation=false"
    match=$(echo "$ADMIN_BODY" | jq --arg n "$name" '[.[] | select((.username | ascii_downcase) == ($n | ascii_downcase))]')
    if [[ "$(echo "$match" | jq 'length')" -eq 0 ]]; then
      echo "not-found  $name"
      continue
    fi
    jq --argjson m "$match" '. + $m' "$WORK_DIR/users.json" > "$WORK_DIR/u.tmp" && mv "$WORK_DIR/u.tmp" "$WORK_DIR/users.json"
  done
fi

EXCLUDES_JSON=$(printf '%s\n' "${EXCLUDES[@]+"${EXCLUDES[@]}"}" | jq -R 'select(. != "") | ascii_downcase' | jq -s '.')
TOTAL=$(jq 'length' "$WORK_DIR/users.json")
echo "Realm $REALM at $KEYCLOAK_BASE: $TOTAL target user(s). $([[ "$APPLY" == true ]] && echo "APPLYING changes." || echo "Dry run; pass --apply to make changes.")"

n_flag=0; n_already=0; n_skip=0; n_fail=0
while IFS= read -r user; do
  id=$(echo "$user" | jq -r '.id')
  name=$(echo "$user" | jq -r '.username')
  lname=$(echo "$name" | tr '[:upper:]' '[:lower:]')

  if echo "$EXCLUDES_JSON" | jq -e --arg n "$lname" 'index($n) != null' > /dev/null; then
    echo "skip       $name (excluded)"; n_skip=$((n_skip + 1)); continue
  fi
  if [[ "$lname" == service-account-* ]]; then
    echo "skip       $name (client service account)"; n_skip=$((n_skip + 1)); continue
  fi
  if [[ "$(echo "$user" | jq -r '.enabled')" != "true" ]]; then
    echo "skip       $name (disabled)"; n_skip=$((n_skip + 1)); continue
  fi
  if [[ "$INCLUDE_NO_PASSWORD" == false ]]; then
    admin_get_ok "users/$id/credentials"
    if ! echo "$ADMIN_BODY" | jq -e 'any(.[]; .type == "password")' > /dev/null; then
      echo "skip       $name (no password credential)"; n_skip=$((n_skip + 1)); continue
    fi
  fi
  has_action=false
  if echo "$user" | jq -e --arg a "$ACTION" '(.requiredActions // []) | index($a) != null' > /dev/null; then
    has_action=true
  fi

  steps=()
  [[ "$RANDOM_PASSWORD" == true ]] && steps+=("random-password")
  [[ "$RANDOM_PASSWORD" == false && "$has_action" == false ]] && steps+=("update-password")
  [[ "$LOGOUT" == true ]] && steps+=("logout")
  if [[ ${#steps[@]} -eq 0 ]]; then
    echo "already    $name"; n_already=$((n_already + 1)); continue
  fi

  if [[ "$APPLY" == false ]]; then
    echo "would      $name: ${steps[*]}"; n_flag=$((n_flag + 1)); continue
  fi

  failed=false
  for step in "${steps[@]}"; do
    case "$step" in
      random-password)
        # temporary=true also adds UPDATE_PASSWORD to the user.
        body=$(jq -nc --arg v "$(random_password)" '{type: "password", value: $v, temporary: true}')
        admin_call PUT "users/$id/reset-password" "$body"
        body="" ;;
      update-password)
        body=$(echo "$user" | jq -c --arg a "$ACTION" '{requiredActions: ((.requiredActions // []) + [$a] | unique)}')
        admin_call PUT "users/$id" "$body" ;;
      logout)
        admin_call POST "users/$id/logout" ;;
    esac
    if [[ "$ADMIN_CODE" != "204" ]]; then
      echo "FAILED     $name: $step ($ADMIN_CODE): $ADMIN_BODY"; failed=true; break
    fi
  done
  if [[ "$failed" == true ]]; then
    n_fail=$((n_fail + 1))
  else
    echo "done       $name: ${steps[*]}"; n_flag=$((n_flag + 1))
  fi
done < <(jq -c '.[]' "$WORK_DIR/users.json")

echo
echo "$([[ "$APPLY" == true ]] && echo "Updated" || echo "Would update"): $n_flag  nothing to do: $n_already  skipped: $n_skip  failed: $n_fail"
[[ "$n_fail" -eq 0 ]]
