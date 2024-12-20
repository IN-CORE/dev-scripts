import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
import incoreuser
from newemail import send_email, get_email_template

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

admin_list = os.getenv("ADMIN_LIST").split(",")
admin_username = os.getenv("KEYCLOAK_USERNAME")
admin_password = os.getenv("KEYCLOAK_PASSWORD")

incoreuser.server_url = os.getenv("KEYCLOAK_URL")
approve_app_url = os.getenv("APPROVE_APP_URL")

from_email = os.getenv("EMAIL_FROM")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))


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


@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    user_approval = incoreuser.IncoreUserApproval.init_with_token(token)
    return render_template('index.html', users=user_approval.unapproved_users, blacklisted_users=user_approval.blacklisted_users)

@app.route('/approve/<user_id>', methods=['POST'])
def approve(user_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    user_approval = incoreuser.IncoreUserApproval.init_with_token(token)
    if user_approval.approve_user_by_id(user_id):
        flash('User approved successfully', 'success')
        # Send an email to the user
        user = user_approval.get_user_by_id(user_id)

        success, user_info = send_welcome_email(user)
        if success:
            flash('Email sent successfully to '+user_info, 'success')
        else:
            flash('Failed to send email to '+user_info, 'danger')        
    else:
        flash('Failed to approve user', 'danger')

    return redirect(url_for('index'))

def send_welcome_email(user):
    to_email = user['email']
    name = user['firstName']+" "+user['lastName']
    username = user['username']
    user_info = f"{name} ({username}, {to_email})"

    subject = "Your IN-CORE account has been approved"
    template = get_email_template("templates/simplified_welcome_email_inlined.html")
    body = template.render({"name": name, "username": user['username']})

    return send_email(subject, body, to_email, from_email, smtp_server, smtp_port), user_info


if __name__ == '__main__':
    app.run(debug=False)