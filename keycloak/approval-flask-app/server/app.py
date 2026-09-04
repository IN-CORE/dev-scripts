import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import timedelta
import incoreuser
import mailinglist
from newemail import send_email, get_email_template

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

admin_list = [email.strip() for email in os.getenv("ADMIN_LIST", "").split(",") if email.strip()]
admin_username = os.getenv("KEYCLOAK_USERNAME")
admin_password = os.getenv("KEYCLOAK_PASSWORD")

incoreuser.server_url = os.getenv("KEYCLOAK_URL")
approve_app_url = os.getenv("APPROVE_APP_URL")

from_email = os.getenv("EMAIL_FROM")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", "25"))

if mailinglist.is_configured():
    print(f"Mailing list subscription enabled for list {mailinglist.list_name}")
else:
    print("Mailing list subscription disabled (SYMPA_* environment variables not set)")


def check_new_users():
    token = incoreuser.IncoreUserApproval.get_keycloak_admin_token(admin_username, admin_password)
    user_approval = incoreuser.IncoreUserApproval.init_with_token(token)
    if len(user_approval.unapproved_users) > 0:
        send_noti_email(admin_list, user_approval.unapproved_users)
        return True
    return False

def send_noti_email(to_email_list, users):
    subject = "IN-CORE New users waiting for approval"

    template = get_email_template("templates/new_users_email_inlined.html")
    body = template.render({"users": users, "approve_app_url": approve_app_url})

    return send_email(subject, body, to_email_list, from_email, smtp_server, smtp_port), to_email_list

sched = BackgroundScheduler(daemon=True)
sched.add_job(check_new_users, 'interval', hours=6)
sched.start()

app = Flask(__name__)
app.secret_key = 'incore'

# Set session timeout to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


@app.route('/approval/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_username = request.form['username']
        admin_password = request.form['password']

        # Validate credentials 
        token = incoreuser.IncoreUserApproval.get_keycloak_admin_token(admin_username, admin_password)
        if token != None:
            session['token'] = token
            session.permanent = True  # Mark the session as permanent

            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/approval/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/approval/healthz')
def healthz():
    # Add any specific checks for the application's health
    health_status = {"status": "healthy"}
    return jsonify(health_status), 200    

@app.route('/approval/')
def index():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    user_approval = incoreuser.IncoreUserApproval.init_with_token(token)
    return render_template('index.html', users=user_approval.unapproved_users, blacklisted_users=user_approval.blacklisted_users)

@app.route('/approval/approve/<user_id>', methods=['POST'])
def approve(user_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    user_approval = incoreuser.IncoreUserApproval.init_with_token(token)
    if user_approval.approve_user_by_id(user_id):
        flash('User approved successfully', 'success')
        user = user_approval.get_user_by_id(user_id)
        if user is None:
            flash('User approved, but the user details could not be loaded. No welcome '
                  'email was sent and the user was not added to the mailing list.', 'warning')
        else:
            handle_post_approval(user, user_approval)
    else:
        flash('Failed to approve user', 'danger')

    return redirect(url_for('index'))

def handle_post_approval(user, user_approval):
    """Everything that follows a successful Keycloak approval. Takes a plain user
    dict so the skip and failure branches can be exercised without approving a
    real user."""
    to_email = user.get('email')
    if not to_email:
        flash('User approved, but there is no email address on file. No welcome email '
              'was sent and the user was not added to the mailing list.', 'warning')
        return

    name = ((user.get('firstName') or "")+" "+(user.get('lastName') or "")).strip()

    # Subscribe first so the welcome email can tell the user whether they are on
    # the list instead of promising a subscription that failed.
    subscribed = subscribe_to_mailing_list(user, to_email, name, user_approval)

    success, user_info = send_welcome_email(user, subscribed)
    if success:
        flash('Email sent successfully to '+user_info, 'success')
    else:
        flash('Failed to send email to '+user_info, 'danger')

def subscribe_to_mailing_list(user, to_email, name, user_approval):
    if not mailinglist.is_configured():
        print("Sympa is not configured, skipping mailing list subscription")
        return False

    # The approve form is only rendered for users that passed the blacklist, so
    # this only catches a hand crafted request. Worth checking anyway: a junk
    # address on a shared mailing list is harder to undo than a junk email.
    if user_approval.check_blacklist(to_email):
        flash(f'User approved, but {to_email} matches the blacklist, so it was not '
              f'added to the mailing list {mailinglist.list_name}.', 'warning')
        return False

    success, message = mailinglist.add_subscriber(to_email, name)
    if success:
        flash(message, 'success')
        return True

    flash(f'User approved. {message}. Please add the address to the mailing list '
          f'manually.', 'warning')
    notify_admins_list_failure(user, to_email, name, mailinglist.list_name, message)
    return False

def notify_admins_list_failure(user, to_email, name, list_name, error_message):
    if not admin_list:
        flash('ADMIN_LIST is not configured, so the admins were not emailed about '
              'the failure above.', 'danger')
        return False

    success = False
    try:
        subject = "IN-CORE Mailing list subscription failed"

        template = get_email_template("templates/list_subscription_failed_email_inlined.html")
        body = template.render({"name": name, "username": user.get('username'),
                                "email": to_email, "list_name": list_name,
                                "error_message": error_message,
                                "approve_app_url": approve_app_url})

        success = send_email(subject, body, admin_list, from_email, smtp_server, smtp_port)
    except Exception as e:
        # This runs after the user has already been approved, so a failure here
        # must not turn a working approval into a server error.
        print(f"Failed to send mailing list failure notification: {e}")

    if not success:
        flash('The admins could not be emailed about the failure above.', 'danger')
    return success

def send_welcome_email(user, list_subscribed=False):
    to_email = user.get('email')
    name = ((user.get('firstName') or "")+" "+(user.get('lastName') or "")).strip()
    username = user.get('username')
    user_info = f"{name} ({username}, {to_email})"

    subject = "Your IN-CORE account has been approved"
    template = get_email_template("templates/simplified_welcome_email_inlined.html")
    body = template.render({"name": name, "username": username,
                            "list_subscribed": list_subscribed,
                            "list_name": mailinglist.list_name})

    return send_email(subject, body, to_email, from_email, smtp_server, smtp_port), user_info


if __name__ == '__main__':
    app.run(debug=False)
