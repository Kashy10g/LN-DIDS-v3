#!/usr/bin/env python3
import smtplib
import ssl
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

try:
    from config import EMAIL
except Exception:
    EMAIL = {}

def send_email_with_attachments(to_addr, subject, body, attachments=None):
    """
    Compatible with app.py expected call signature:
        send_email_with_attachments(to_addr, subject, body, attachments)

    Returns: (True, "OK") or (False, "error message")
    """

    sender_email = EMAIL.get("sender_email")
    sender_password = EMAIL.get("app_password")
    smtp_server = EMAIL.get("smtp_server", "smtp.gmail.com")
    smtp_port = EMAIL.get("smtp_port", 587)
    use_tls = EMAIL.get("use_tls", True)

    if not sender_email or not sender_password:
        return False, "Email configuration missing sender_email or app_password"

    # ensure list for recipients
    if isinstance(to_addr, str):
        receivers = [to_addr]
    else:
        receivers = list(to_addr)

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach files
    attachments = attachments or []
    for file_path in attachments:
        try:
            part = MIMEBase("application", "octet-stream")
            with open(file_path, "rb") as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={file_path.split('/')[-1]}"
            )
            msg.attach(part)
        except Exception as e:
            return False, f"Attachment error: {e}"

    # Send email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            if use_tls:
                server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receivers, msg.as_string())
        return True, "OK"

    except Exception as e:
        return False, str(e)
