# IN-CORE User Approval App

## Description
A small Flask app that IN-CORE admins use to approve new users who signed up on the
IN-CORE platform. New signups land in a Keycloak group named `0unapproved`; this app lists
them and lets an admin approve each one from the browser.

Approving a user does three things:

1. Moves the user from the `0unapproved` Keycloak group to `incore_user`.
2. Subscribes the user's email address to the `incore-announce` mailing list on
   `lists.illinois.edu` (see [Mailing list subscription](#7-mailing-list-subscription)).
3. Sends the user the IN-CORE welcome email.

The Keycloak approval is what gates the other two: if it fails, nothing else runs. If the
mailing list subscription fails, the approval and the welcome email still stand, the admin
sees a warning, and the admins are emailed so the address can be added by hand.

Users whose email domain is on a blacklist (currently `@qq.com`, in `incoreuser.py`) are
listed separately and are never subscribed to the mailing list.

The app also runs a background job every 6 hours that emails `ADMIN_LIST` when there are
users waiting for approval.

### Routes

| Route | Method | Description |
| --- | --- | --- |
| `/approval/login` | GET, POST | Log in with Keycloak admin credentials |
| `/approval/logout` | GET | Clear the session |
| `/approval/` | GET | List unapproved and blacklisted users |
| `/approval/approve/<user_id>` | POST | Approve one user |
| `/approval/healthz` | GET | Health check for Kubernetes probes |

## How to Use

### 1. Environment Variables

Keycloak and email (all required):

- **KEYCLOAK_URL**: Base URL of the Keycloak server, including the auth path
  (e.g. `https://tools.in-core.org/auth/`).
- **KEYCLOAK_USERNAME**: Keycloak admin username, used by the 6 hour background job.
- **KEYCLOAK_PASSWORD**: Keycloak admin password, used by the 6 hour background job.
- **ADMIN_LIST**: Comma-separated admins to notify (e.g. `user1@illinois.edu,user2@illinois.edu`).
- **APPROVE_APP_URL**: Public URL of this app, used as the link in notification emails.
- **EMAIL_FROM**: The "From" address for outgoing email.
- **SMTP_SERVER**: SMTP server used to send email (e.g. `outbound-relays.techservices.illinois.edu`).
- **SMTP_PORT**: SMTP port (defaults to `25`).

Mailing list, via the Sympa SOAP API:

- **SYMPA_APP_NAME**: Sympa trusted application name.
- **SYMPA_APP_PASSWORD**: Sympa trusted application password. This is a secret.
- **SYMPA_PROXY_USER_EMAIL**: The address the app acts as. It must be an **owner** of the
  list, because the list's `add` scenario authorizes against it. Use a role address rather
  than an individual's.
- **SYMPA_SOAP_URL**: SOAP endpoint (defaults to `https://lists.illinois.edu/sympasoap`).
- **SYMPA_LIST_NAME**: The bare, lowercase list name — `incore-announce`, **not** the full
  `incore-announce@lists.illinois.edu` address (defaults to `incore-announce`).
- **SYMPA_TIMEOUT**: Read timeout in seconds for the SOAP call (defaults to `20`).

**The first three `SYMPA_*` variables are optional as a group.** If any of them is missing,
mailing list subscription is skipped entirely and the app behaves exactly as it did before
the feature existed — approval and the welcome email still work, and no warning is shown.
The app prints which mode it is in at startup. This means an existing deployment keeps
working unchanged until the Sympa credentials are added.

### 2. Example environment variables
```bash
KEYCLOAK_URL=https://tools.in-core.org/auth/
KEYCLOAK_USERNAME=admin
KEYCLOAK_PASSWORD=your_password
ADMIN_LIST=user1@illinois.edu,user2@illinois.edu
APPROVE_APP_URL=https://tools.in-core.org/approval/
EMAIL_FROM=no-reply@illinois.edu
SMTP_SERVER=outbound-relays.techservices.illinois.edu
SMTP_PORT=25
SYMPA_APP_NAME=incore-approval-app
SYMPA_APP_PASSWORD=your_sympa_app_password
SYMPA_PROXY_USER_EMAIL=incore-dev@lists.illinois.edu
SYMPA_SOAP_URL=https://lists.illinois.edu/sympasoap
SYMPA_LIST_NAME=incore-announce
SYMPA_TIMEOUT=20
```

These can go in a `server/.env` file for local development. Note that `.dockerignore`
excludes `*env*`, so `.env` is deliberately **not** baked into the image — in a real
deployment the variables have to be supplied at runtime, and `SYMPA_APP_PASSWORD` and
`KEYCLOAK_PASSWORD` should come from a Kubernetes Secret.

### 3. Running Locally
```bash
cd server
pip install -r requirements.txt
flask run
```

Run it from the `server` directory: the email templates are loaded by relative path
(`templates/...`), so the working directory has to be the one holding `templates/`.

### 4. Docker
```bash
docker build -t approval-app .
docker run --rm -p 5000:5000 --env-file server/.env approval-app
```

CI builds this image as `hub.ncsa.illinois.edu/incore/approval-app` — see
`.github/workflows/approval-app-docker.yml`.

### 5. Prerequisites
- Python 3
- Flask
- python-keycloak
- apscheduler
- python-dotenv
- requests

There is a `requirements.txt` file in `server/` that contains the required packages:
```bash
pip install -r server/requirements.txt
```

### 6. Usage in Kubernetes

This is a long-running app rather than a scheduled job, so it wants a Deployment and a
Service:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: approval-app
spec:
  # Keep this at 1. The 6 hour "users waiting for approval" job runs in-process, so
  # every extra replica sends the admins another copy of the same notification email.
  replicas: 1
  selector:
    matchLabels:
      app: approval-app
  template:
    metadata:
      labels:
        app: approval-app
    spec:
      containers:
        - name: approval-app
          image: hub.ncsa.illinois.edu/incore/approval-app:latest
          ports:
            - containerPort: 5000
          readinessProbe:
            httpGet:
              path: /approval/healthz
              port: 5000
          livenessProbe:
            httpGet:
              path: /approval/healthz
              port: 5000
          env:
            - name: KEYCLOAK_URL
              value: "https://tools.in-core.org/auth/"
            - name: KEYCLOAK_USERNAME
              value: "admin"
            - name: KEYCLOAK_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: approval-app-secrets
                  key: keycloak-password
            - name: ADMIN_LIST
              value: "user1@illinois.edu,user2@illinois.edu"
            - name: APPROVE_APP_URL
              value: "https://tools.in-core.org/approval/"
            - name: EMAIL_FROM
              value: "no-reply@illinois.edu"
            - name: SMTP_SERVER
              value: "outbound-relays.techservices.illinois.edu"
            - name: SMTP_PORT
              value: "25"
            - name: SYMPA_APP_NAME
              value: "incore-approval-app"
            - name: SYMPA_APP_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: approval-app-secrets
                  key: sympa-app-password
            - name: SYMPA_PROXY_USER_EMAIL
              value: "incore-dev@lists.illinois.edu"
            - name: SYMPA_LIST_NAME
              value: "incore-announce"
---
apiVersion: v1
kind: Service
metadata:
  name: approval-app
spec:
  selector:
    app: approval-app
  ports:
    - port: 80
      targetPort: 5000
```

Every route is hardcoded under the `/approval` prefix, so an Ingress should route
`/approval` to this Service without rewriting the path.

### 7. Mailing list subscription

Subscription goes through the Sympa SOAP API at `https://lists.illinois.edu/sympasoap`,
using the `authenticateRemoteAppAndRun` operation to run `add` as a **trusted
application**. `mailinglist.py` builds the SOAP envelope by hand, because Sympa's WSDL is
rpc/encoded and its `parameters` argument is a SOAP-encoded array, which the common Python
SOAP clients do not serialize correctly.

#### Getting credentials

The trusted application has to be registered by Illinois Technology Services, who manage
`lists.illinois.edu`. Ask them for an entry like:

```
trusted_application
name                 incore-approval-app
md5password          <md5 of the password they issue>
proxy_for_variables  USER_EMAIL
allow_commands       add,review
```

Two details are worth confirming with them explicitly, because the same unhelpful
`Authentication failed` fault covers both: that `proxy_for_variables` includes
`USER_EMAIL`, and that `allow_commands` (if set at all) includes `add`. Also make sure
`SYMPA_PROXY_USER_EMAIL` is an owner of the list.

#### Behavior

- Sympa's own "you have been added" notice is suppressed, since the app sends its own
  welcome email. That welcome email tells the user they were subscribed and links to the
  list page so they can unsubscribe.
- A user who is already on the list is treated as a success, so re-approving is harmless.
- Sympa answers `true` even when its `add` scenario only queued a confirmation request and
  subscribed nobody, so every add is confirmed afterwards with an `amI` membership check.
  `amI` needs no credentials, which also makes it a convenient way to check the list.
- On failure the approval and the welcome email still succeed. The admin sees a warning,
  and `ADMIN_LIST` receives a "Mailing list subscription failed" email naming the user, the
  list and the error. The fix is to add the address by hand at
  `https://lists.illinois.edu/lists/info/incore-announce`; there is no automatic retry.

#### Testing it

`mailinglist.py` can be run directly. Use your **own** address, and prefer a scratch list
over `incore-announce` for anything beyond a membership check:

```bash
cd server
python mailinglist.py you@illinois.edu "Your Name"
```

It prints membership before and after the add. Running it twice exercises the
already-subscribed path. `mailinglist.remove_subscriber(email)` cleans up afterwards.

A membership check on its own needs no credentials at all:
```bash
python -c "import mailinglist; print(mailinglist.is_subscriber('you@illinois.edu'))"
```

### 8. Error Handling

Failures are printed to stdout, so they show up in `kubectl logs`. The mailing list client
never raises: it returns a success flag and a short message, because it runs after the user
has already been approved in Keycloak and an exception there would leave the admin unable
to tell whether the approval took. Sympa's raw fault text is logged in full but shortened
before it reaches a flash message or an email.

### Note: templates

The email templates come in pairs, `<name>.html` and `<name>_inlined.html`. Only the
`_inlined` versions are loaded by the code; the plain ones are the sources those were
generated from by running them through a CSS inliner. Keep both in sync when editing.
`list_subscription_failed_email_inlined.html` is inlined-only, since it has no `<style>`
block to inline.
