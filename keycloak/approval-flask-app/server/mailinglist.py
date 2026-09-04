import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import requests
from dotenv import load_dotenv

# app.py calls load_dotenv() after its imports, so a module that reads os.getenv at
# import time would see nothing from .env. Load it here too; it is idempotent.
load_dotenv()

soap_url = os.getenv("SYMPA_SOAP_URL", "https://lists.illinois.edu/sympasoap")
app_name = os.getenv("SYMPA_APP_NAME")
app_password = os.getenv("SYMPA_APP_PASSWORD")
proxy_user_email = os.getenv("SYMPA_PROXY_USER_EMAIL")
list_name = os.getenv("SYMPA_LIST_NAME", "incore-announce")
soap_timeout = int(os.getenv("SYMPA_TIMEOUT", "20"))

# Sympa is SOAP::Lite over rpc/encoded, so the request is built by hand: the
# parameters array has to be a SOAP-ENC:Array with an arrayType attribute or the
# server decodes it as a hash and scrambles the positional arguments.
SOAP_ENVELOPE = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<soapenv:Envelope'
    ' xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
    ' xmlns:xsd="http://www.w3.org/2001/XMLSchema"'
    ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    ' xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">'
    '<soapenv:Body soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    '<urn:%(operation)s xmlns:urn="urn:sympasoap">%(parts)s</urn:%(operation)s>'
    '</soapenv:Body></soapenv:Envelope>'
)


def is_configured():
    return bool(app_name) and bool(app_password) and bool(proxy_user_email)


def string_part(name, value):
    return '<%s xsi:type="xsd:string">%s</%s>' % (
        name, escape("" if value is None else str(value)), name)


def array_part(name, values):
    items = "".join(string_part("item", value) for value in values)
    return '<%s xsi:type="soapenc:Array" soapenc:arrayType="xsd:string[%d]">%s</%s>' % (
        name, len(values), items, name)


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def clean_reason(text):
    """Shorten a Sympa fault into something short enough to flash and email.

    Sympa answers some failures with a raw Perl error that carries a server side
    file path ("... at /usr/share/sympa/lib/... line 379."), which is noise to an
    admin, so the location is dropped and the rest is truncated. The full text is
    still printed to the log by the caller.
    """
    text = " ".join((text or "").split())
    location = text.find(" at /")
    if location != -1:
        text = text[:location]
    if len(text) > 200:
        text = text[:200] + "..."
    # The caller composes these into a sentence, so drop Sympa's own full stop.
    return text.rstrip(".")


def soap_call(operation, parts):
    """Post one SOAP request.

    Returns (values, fault): values is the list of non-empty leaf strings in the
    response body, fault is a dict of the SOAP fault children or None. Raises on
    transport and parse errors.
    """
    body = (SOAP_ENVELOPE % {"operation": operation, "parts": parts}).encode("utf-8")
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '"urn:sympasoap#%s"' % operation,
    }
    response = requests.post(soap_url, data=body, headers=headers,
                             timeout=(5, soap_timeout))
    try:
        # Sympa returns faults with HTTP 500, so the body is parsed either way.
        root = ET.fromstring(response.content)
    except ET.ParseError:
        raise Exception("HTTP %s from Sympa: %s" % (
            response.status_code, response.text[:200]))

    for element in root.iter():
        if local_name(element.tag) == "Fault":
            fault = {}
            for child in element:
                fault[local_name(child.tag)] = (child.text or "").strip()
            return None, fault

    values = [(e.text or "").strip() for e in root.iter()
              if len(e) == 0 and (e.text or "").strip()]
    return values, None


def trusted_app_call(service, parameters):
    parts = (string_part("appname", app_name)
             + string_part("apppassword", app_password)
             + string_part("vars", "USER_EMAIL=%s" % proxy_user_email)
             + string_part("service", service)
             + array_part("parameters", parameters))
    return soap_call("authenticateRemoteAppAndRun", parts)


def is_subscriber(email, target_list=None):
    """Check list membership. Needs no credentials. Returns True, False or None
    when the check itself failed."""
    target_list = target_list or list_name
    parts = (string_part("list", target_list)
             + string_part("function", "subscriber")
             + string_part("user", email))
    try:
        values, fault = soap_call("amI", parts)
    except Exception as e:
        print(f"Failed to check if {email} is on {target_list}: {e}")
        return None

    if fault is not None:
        print(f"Failed to check if {email} is on {target_list}: "
              f"{fault.get('faultstring')} ({fault.get('detail')})")
        return None

    return bool(values) and values[0].lower() in ("true", "1")


def add_subscriber(email, name=None, target_list=None, verify=True):
    """Add one address to the mailing list. Returns (success, message).

    Never raises: the caller runs after the user has already been approved in
    Keycloak, so a failure here has to stay a message rather than an exception.
    Messages are shown to admins and emailed, so they must not carry the request
    envelope (it holds the application password) or a traceback.
    """
    # add(), unlike amI(), does not lowercase the list name itself.
    target_list = (target_list or list_name).lower()

    if not is_configured():
        print("Sympa is not configured, skipping mailing list subscription")
        return False, "Mailing list is not configured"
    if not email:
        return False, "No email address to subscribe"

    # Positional: list, email, gecos, quiet. quiet='1' suppresses Sympa's own
    # notice because the app sends its own welcome email.
    parameters = [target_list, email, name or "", "1"]
    try:
        values, fault = trusted_app_call("add", parameters)
    except Exception as e:
        print(f"Failed to add {email} to {target_list}: {e}")
        return False, f"Failed to add {email} to {target_list}"

    if fault is not None:
        detail = fault.get("detail", "")
        # faultstring is the literal "Undef" for every user level error, so the
        # already-subscribed case can only be told apart by the detail text.
        if "already subscrib" in detail.lower():
            print(f"{email} is already subscribed to {target_list}")
            return True, f"{email} is already on {target_list}"
        reason = clean_reason(detail or fault.get("faultstring")) or "unknown error"
        print(f"Failed to add {email} to {target_list}: "
              f"{fault.get('faultstring')} ({detail})")
        return False, f"Failed to add {email} to {target_list}: {reason}"

    if values and values[0].lower() in ("false", "0"):
        return False, f"Sympa refused to add {email} to {target_list}"

    # Sympa answers "true" even when its add scenario only queued a confirmation
    # request and subscribed nobody, so a successful call is confirmed separately.
    if verify and is_subscriber(email, target_list) is False:
        print(f"Sympa accepted the add but {email} is not on {target_list}")
        return False, (f"{email} was not added to {target_list} "
                       f"(a confirmation may be pending)")

    print(f"{email} added to {target_list}")
    return True, f"{email} added to {target_list}"


def remove_subscriber(email, target_list=None):
    """Remove one address from the list. Mainly for cleaning up after a test."""
    target_list = (target_list or list_name).lower()

    if not is_configured():
        print("Sympa is not configured, skipping mailing list removal")
        return False, "Mailing list is not configured"

    try:
        values, fault = trusted_app_call("del", [target_list, email, "1"])
    except Exception as e:
        print(f"Failed to remove {email} from {target_list}: {e}")
        return False, f"Failed to remove {email} from {target_list}"

    if fault is not None:
        reason = clean_reason(
            fault.get("detail") or fault.get("faultstring")) or "unknown error"
        print(f"Failed to remove {email} from {target_list}: "
              f"{fault.get('faultstring')} ({fault.get('detail')})")
        return False, f"Failed to remove {email} from {target_list}: {reason}"

    print(f"{email} removed from {target_list}")
    return True, f"{email} removed from {target_list}"


def get_subscribers(target_list=None):
    """List the current members. Needs 'review' in the application's
    allow_commands. Returns a list of emails, or None when the call failed."""
    target_list = (target_list or list_name).lower()

    if not is_configured():
        print("Sympa is not configured, skipping mailing list review")
        return None

    try:
        values, fault = trusted_app_call("review", [target_list])
    except Exception as e:
        print(f"Failed to review {target_list}: {e}")
        return None

    if fault is not None:
        print(f"Failed to review {target_list}: "
              f"{fault.get('faultstring')} ({fault.get('detail')})")
        return None

    # Sympa returns the single value "no_subscribers" for an empty list.
    if values == ["no_subscribers"]:
        return []
    return values


# Example usage
if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else None
    name = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"list: {list_name}")
    print(f"configured: {is_configured()}")
    print(f"proxy user: {proxy_user_email}")

    if email is None:
        print("Usage: python mailinglist.py <email> [name]")
    else:
        print(f"before: {is_subscriber(email)}")
        print(add_subscriber(email, name))
        print(f"after : {is_subscriber(email)}")
