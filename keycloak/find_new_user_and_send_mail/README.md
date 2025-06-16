# Keycloak Email Report Script

## Description
This scripts retrieve user information from a specified Keycloak group and sends the results via email. The script authenticates with Keycloak, queries a given group for its members, and compiles a list of users in CSV format. The CSV list is then emailed to a set of specified recipients.
- There are two scripts one is a shell script and the other is a python script. These are basically the same scripts but written in different languages.
- In this READEME.md file, we will be discussing the python script.
- Python script is more flexible and can be easily integrated with other systems and used for the kubernetes cronjob.
- The script uses the Keycloak Admin REST API to fetch the group members and sends the report via email using SMTP.
- The script can be used in a Kubernetes CronJob to schedule periodic executions.

## How to Use

### 1. Environment Variables
Before running the script, ensure the following environment variables are set correctly:

- **KEYCLOAK_URL**: The base URL of your Keycloak server (e.g., `https://keycloak.example.com`).
- **KEYCLOAK_USERNAME**: Keycloak admin username.
- **KEYCLOAK_PASSWORD**: Keycloak admin password.
- **REALM**: The Keycloak realm where your group resides.
- **GROUP**: The name of the Keycloak group you want to query.
- **EMAIL_RECIPIENTS**: A comma-separated list of email recipients (e.g., `user1@example.com,user2@example.com`).
- **EMAIL_SUBJECT**: The subject of the email.
- **EMAIL_BODY**: The body content of the email (used as additional context or description).
- **EMAIL_FROM**: The "From" email address to use when sending the report.
- **SMTP_SERVER**: The SMTP server to be used for sending the email (e.g., `smtp.example.com`).
- **SMTP_PORT**: The port of the SMTP server (e.g., `587`).

### 2. Example environment variables
```bash
KEYCLOAK_URL=https://keycloak.example.com
KEYCLOAK_USERNAME=admin
KEYCLOAK_PASSWORD=your_password
REALM=your_realm
GROUP=your_group
EMAIL_RECIPIENTS=user1@example.com,user2@example.com
EMAIL_SUBJECT=Keycloak Group User Report
EMAIL_BODY=This is the list of users in the specified group.
EMAIL_FROM=noreply@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
```

### 3. Running the Script
Run the script using the following command:
```bash
python3 find_new_users_and_mail.py
```

### 4. Prerequisites
- Python 3
- requests
- python-dotenv
- smtplib
- email

There is a `requirements.txt` file in the repository that contains the required packages. You can install them using the following command:
```bash
pip install -r requirements.txt
```

### 5. Error Handling
If any step fails (e.g., authentication, group ID retrieval, fetching members), an exception is raised and the error is printed to the console.

### 6. Usage in a Kubernetes CronJob
The script can be used in a Kubernetes CronJob to schedule periodic executions (e.g., every 15 minutes). Below is an example Kubernetes CronJob YAML configuration:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ include "incore.fullname" . }}-new-user-alert
  labels:
    {{- include "incore.labels" . | nindent 4 }}
spec:
  schedule: "0 8,16 * * 1-5"  # Runs at 8 AM and 4 PM, Monday to Friday
  startingDeadlineSeconds: 3600
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 1
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 1
      template:
        spec:
          {{- with .Values.imagePullSecrets }}
          imagePullSecrets:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          containers:
            - name: new-user-alert-job
              image: python:3.9-slim
              imagePullPolicy: IfNotPresent
              command: ["python"]
              args:
                - "/usr/src/app/find_new_users_and_mail.py"
              env:
                - name: KEYCLOAK_URL
                  value: "https://keycloak.example.com"
                - name: KEYCLOAK_USERNAME
                  value: "admin"
                - name: KEYCLOAK_PASSWORD
                  value: "your_password"
                - name: REALM
                  value: "your_realm"
                - name: GROUP
                  value: "your_group"
                - name: EMAIL_RECIPIENTS
                  value: "user1@example.com,user2@example.com"
                - name: EMAIL_SUBJECT
                  value: "Keycloak Group User Report"
                - name: EMAIL_BODY
                  value: "This is the list of users in the specified group."
                - name: EMAIL_FROM
                  value: "noreply@example.com"
                - name: SMTP_SERVER
                  value: "smtp.example.com"
                - name: SMTP_PORT
                  value: "587"
          restartPolicy: Never
```

### Note: In this configuration

- **Python Docker Image**: Replace the image name (`python:3.9-slim`) with your Python Docker image that contains the script if needed. There is a Dockerfile in the repository that can be used to build a custom image.
- **Script Location**: You can mount the script from a ConfigMap or create a container to have the script in it. You need to create a ConfigMap containing your script and mount it.

