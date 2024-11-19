import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

# Read the Jinja2 email template
def get_email_template(filename):        
    with open("templates/simplified_welcome_email_inlined.html", "r") as file:
        template_str = file.read()

    jinja_template = Template(template_str)
    return jinja_template

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'html'))
    success = False
    try:
        # Set up the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port,timeout=10)
        server.ehlo()
        server.starttls()
        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully")
        success = True

    except Exception as e:
        print(f"Failed to send email: {e}")
        success = False

    finally:
        server.quit()
        print(f"SMTP server connection closed")
        return success

# Example usage
if __name__ == "__main__":
    subject = "Your IN-CORE account has been approved!"
    #body = "Your IN-CORE account has been approved. You can now login to the IN-CORE platform."
    to_email = "sakibkhan@mitre.org"
    from_email = "no-reply@illinois.edu"
    smtp_server = "outbound-relays.techservices.illinois.edu"
    smtp_port = 25
    # smtp_user = "your_email@example.com"
    # smtp_password = "your_password"

    body = get_email_template.render({"name": "Sakib Khan", "username": "sakib"})
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port)