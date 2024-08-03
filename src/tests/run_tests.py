import json
import os
from typing import Any

from easy_smtp import SMTPHandler, SMTPCredentials


curdir = os.path.dirname(__file__)
filename = input("Enter SMTP Config filename without extension (file must be in same directory as this file):")
with open(os.path.join(curdir, f"{filename}.json"), "r") as f:
    config_dict: dict[str, Any] = json.load(f)
    credentials_dict = config_dict.get("credentials", None)
    recipients = config_dict["recipients"]
    sender = config_dict["sender"]
    smtp_port = config_dict["smtp_port"]
    smtp_server = config_dict["smtp_server"]
    use_tls = config_dict["use_tls"]

if credentials_dict is not None:
    credentials = SMTPCredentials(credentials_dict["username"], credentials_dict["password"])
else:
    credentials = None

handler = SMTPHandler(sender, recipients, smtp_server, smtp_port, use_tls=use_tls, credentials=credentials)


# Send simple mail
print("Send simple mail...")
handler.send_mail("Test message", "Simple test subject")

# Send simple mail with html format
html_body = """
<html>
    <body>
        <h1>Test HTML message</h1>
        <p>This is a test HTML message.</p>        
    </body>
</html>
"""
print("Send simple HTML mail...")
handler.send_mail(html_body, "Simple html test subject", is_html=True)

# Send exception mail
try:
    a = 1 / 0
except Exception as e:
    print("Send exception mail...")
    handler.send_exception_email(e, "Exception test subject")