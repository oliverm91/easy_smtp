from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import traceback
from typing import Optional


@dataclass(slots=True)
class SMTPCredentials:
    username: str
    password: str


@dataclass(slots=True)
class SMTPHandler:
    sender: str
    recipients: str | list[str]
    smtp_server: str
    smtp_port: int
    use_tls: bool = field(default=True)
    credentials: Optional[SMTPCredentials] = field(default=None)    
    
    def __post_init__(self):
        self._check_attributes()
        
    def _check_attributes(self):
        if not isinstance(self.recipients, list) and not isinstance(self.recipients, str):
            raise TypeError(f"recipients must be of type list of strings or string. Got {type(self.recipients)}")
        if isinstance(self.recipients, list):
            for recipient in self.recipients:
                if not isinstance(recipient, str):
                    raise TypeError(f"If recipients is a list, all items in list must be of type string. Got {type(self.recipients)}")
        
        if not isinstance(self.smtp_port, int):
            raise TypeError(f"smtp_port must be of type int. Got {type(self.smtp_port)}")
        
        if not isinstance(self.use_tls, bool):
            raise TypeError(f"use_tls must be of type bool. Got {type(self.use_tls)}")
        
        if not isinstance(self.sender, str):
            raise TypeError(f"sender must be of type str. Got {type(self.sender)}")
        
        if not isinstance(self.smtp_server, str):
            raise TypeError(f"smtp_server must be of type str. Got {type(self.smtp_server)}")
        
        if self.credentials is not None and not isinstance(self.credentials, SMTPCredentials):
            raise TypeError(f"credentials must be of type SMTPCredentials. Got {type(self.credentials)}")

    def send_exception_email(self, exception: Exception, subject: str, post_traceback_html_body: Optional[str]=None):
        tb_str = traceback.format_exc()
        
        if post_traceback_html_body is None:
            post_traceback_html_body = ""

        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #333;
                }}
                h2 {{
                    color: #d9534f;
                }}
                .exception {{
                    font-weight: bold;
                    color: #d9534f;
                }}
                .traceback {{
                    background-color: #f9f2f4;
                    border: 1px solid #d9534f;
                    padding: 10px;
                    font-family: 'Courier New', Courier, monospace;
                    white-space: pre-wrap;
                    color: #333;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <h2>Exception Details</h2>
            <p class="exception">Exception: {exception}</p>
            <p><strong>Traceback:</strong></p>
            <div class="traceback">{tb_str}</div>
            <p>{post_traceback_html_body}</p>
        </body>
        </html>
        """
        
        self.send_mail(body, subject, is_html=True)

    def send_mail(self, body: str, subject: str, is_html: bool = False):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ", ".join(self.recipients)
        msg['Subject'] = subject

        mime_text_subtype = 'html' if is_html else 'plain'
        body = MIMEText(body, mime_text_subtype)
        msg.attach(body)        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            if self.credentials is not None:
                server.login(self.credentials.username, self.credentials.password)
            server.sendmail(self.sender, self.recipients, msg.as_string())