# Keycloak user export

Export IN-CORE Keycloak realm users to JSON, CSV and a plain-text list.

## Prerequisites

- `bash`, `curl`, and `jq`
- Admin credentials for the Keycloak **master** realm (`admin-cli` password grant)

```bash
# prompts silently, so the password is not echoed or saved to shell history
read -rs KEYCLOAK_ADMIN_PASS && export KEYCLOAK_ADMIN_PASS
```

Clear it when you're done with `unset KEYCLOAK_ADMIN_PASS`.

Optional overrides:

| Variable | Default |
|---|---|
| `KEYCLOAK_ADMIN_USER` | `keycloak` |
| `KEYCLOAK_BASE` | `https://tools.in-core.org/auth` (dev: `https://dev.in-core.org/auth`) |
| `KEYCLOAK_REALM` | `In-core` |
| `KEYCLOAK_GROUP` | unset (every user in the realm) |

## Usage

```bash
cd keycloak/export-users

# all users with an email
./export-keycloak-users.sh

# direct members of one group (name, or a full path if the name is not unique)
KEYCLOAK_GROUP=inc-core ./export-keycloak-users.sh
KEYCLOAK_GROUP=/parent/inc-core ./export-keycloak-users.sh

# registered in the last 3 months
./export-keycloak-users.sh --registered-within 3 -o new-users.csv

# registered on or after a date (UTC)
./export-keycloak-users.sh --registered-since 2026-01-01 -o new-users.csv

# logged in within the last 6 months
./export-keycloak-users.sh --active-within 6 -o active-users.csv

# logged in on or after a date (UTC)
./export-keycloak-users.sh --active-since 2026-04-01 -o active-users.csv

# both filters (user must match all)
./export-keycloak-users.sh --registered-since 2026-01-01 --active-within 6 -o both.csv
```

### Options

| Option | Description |
|---|---|
| `--registered-within N` | Keep users whose account was created in the last N months |
| `--registered-since DATE` | Keep users whose account was created on or after `DATE` (`YYYY-MM-DD`, UTC) |
| `--active-within N` | Keep users with a LOGIN event in the last N months |
| `--active-since DATE` | Keep users with a LOGIN event on or after `DATE` (`YYYY-MM-DD`, UTC) |
| `-o`, `--output FILE` | CSV path (default: `users.csv`). The text list uses the same name with a `.txt` extension. |
| `-h`, `--help` | Show help |

Filters can be combined; a user must match every filter you pass. For each kind of filter (registration vs activity), use either the month window or the date — not both.

Activity filters need user events enabled on the realm (Realm settings → Events → User events). Only logins within the realm's event retention window are available.

## Outputs

| File | Contents |
|---|---|
| `users.json` | User list from Keycloak. Every realm user, or only direct members of `KEYCLOAK_GROUP` when that variable is set. Date filters are not applied here. |
| `users.csv` (or `-o` path) | Same users, with an email, after any date filters |
| `users.txt` (or the `-o` path with a `.txt` extension) | One line per CSV row: `email First Last` |

CSV columns:

```
emailAddress,id,username,firstName,lastName,enabled,createdAt,lastLogin
```

- Rows without an email are skipped.
- `createdAt` / `lastLogin` are ISO-8601 UTC timestamps.
- `lastLogin` is filled only when an activity filter (`--active-within` or `--active-since`) is used.
