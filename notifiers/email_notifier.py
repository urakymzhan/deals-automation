import smtplib
from email.mime.text import MIMEText
from config import EMAIL_FROM, EMAIL_TO, GMAIL_APP_PASSWORD


def send_email(subject: str, body: str):
    if not GMAIL_APP_PASSWORD:
        print("[Email] GMAIL_APP_PASSWORD not set. Skipping.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, GMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"[Email] Sent '{subject}'")
    except Exception as e:
        print(f"[Email] Failed to send: {e}")
