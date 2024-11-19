from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
from incoreuser import IncoreUserApproval
from newemail import send_email, get_email_template

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
        token = IncoreUserApproval.get_keycloak_admin_token(admin_username, admin_password)
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

    user_approval = IncoreUserApproval.init_with_token(token)
    return render_template('index.html', users=user_approval.unapproved_users, blacklisted_users=user_approval.blacklisted_users)

@app.route('/approve/<user_id>', methods=['POST'])
def approve(user_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))

    user_approval = IncoreUserApproval.init_with_token(token)
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
    subject = "Your IN-CORE account has been approved"
    from_email = "no-reply@illinois.edu"
    smtp_server = "outbound-relays.techservices.illinois.edu"
    smtp_port = 25
    template = get_email_template("templates/simplified_welcome_email_inlined.html")
    name = user['firstName']+" "+user['lastName']
    body = template.render({"name": name, "username": user['username']})
    to_email = user['email']
    username = user['username']
    user_info = f"{name} ({username}, {to_email})"
    return send_email(subject, body, to_email, from_email, smtp_server, smtp_port), user_info


if __name__ == '__main__':
    app.run(debug=True)