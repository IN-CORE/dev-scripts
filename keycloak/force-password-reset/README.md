# Force a Keycloak password reset

`force-password-reset.sh` makes Keycloak users set a new password at their next login:

1. Adds the `UPDATE_PASSWORD` required action. With `--random-password`, it instead replaces the password with a random one that nobody sees.
2. Signs out the user's sessions, so the change takes effect now instead of when their tokens expire. Turn this off with `--no-logout`.

It runs as a **dry run by default**: nothing changes until you pass `--apply`.

## Prerequisites

- `bash`, `curl` and `jq` (plus `openssl` for `--random-password`)
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

No passwords or secrets go in the script or on the command line. The admin password comes from the environment, and random passwords are sent to Keycloak on stdin and never printed.

## Usage

Try it on yourself and other developers first:

```bash
cd keycloak/force-password-reset

# dry run: shows what would happen
./force-password-reset.sh -u alice -u bob

# apply: required action + sign-out
./force-password-reset.sh -u alice -u bob --apply

# or read usernames from a file (one per line, # comments allowed)
./force-password-reset.sh -f devs.txt --apply
```

Then everyone, skipping service and test accounts:

```bash
./force-password-reset.sh --all -x maestro -x incrtest            # dry run
./force-password-reset.sh --all -x maestro -x incrtest --apply
```

### Options

| Option | Description |
|---|---|
| `-u`, `--user NAME` | Username (exact match). Repeatable. |
| `-f`, `--users-file FILE` | One username per line |
| `--all` | Every user in the realm |
| `-x`, `--exclude NAME` | Username to skip. Repeatable. |
| `--exclude-file FILE` | Usernames to skip, one per line |
| `--random-password` | Also replace the password with a random one (see below) |
| `--no-logout` | Don't sign users out |
| `--include-no-password` | Also act on users with no stored password (e.g. identity-provider-only users) |
| `--apply` | Make the changes |

These users are always skipped: `service-account-*` users, disabled users and, unless you pass `--include-no-password`, users with no password credential.

## Required action vs. random password

| | Required action only (default) | `--random-password` |
|---|---|---|
| How users get back in | Log in with their **current** password, then set a new one | **Forgot password** email only |
| Protects against a leaked password? | No: whoever has the old password can log in and set a new one | Yes: the old password stops working right away |
| Realm needs | Nothing | "Forgot password" enabled and SMTP configured (the script checks both and stops if either is missing) |

Use the default for routine rotation. Use `--random-password` if you think passwords may have leaked.

## Things to know

- **Scripted logins break** (pyincore `IncoreClient` with a username and password, and anything else that uses the password grant). Keycloak refuses them with "Account is not fully set up" until the user changes their password in the browser. Tell users before you run `--all`.
- **Service and test accounts** that log in with a password (`maestro`, `incrtest`, …) must be passed with `-x`, or their automation breaks. Rotate those separately.
- Sign-out ends browser and refresh-token sessions. Offline tokens are tied to sessions too, but already-issued access tokens stay valid until they expire (a few minutes).
- Admin tokens are short-lived. The script refreshes on a 401, so long `--all` runs are fine.
