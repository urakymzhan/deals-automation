from config import NOTIFICATION_METHOD
from .email_notifier import send_email
from .sms_notifier import send_sms


def notify(subject: str, body: str):
    if NOTIFICATION_METHOD == "sms":
        send_sms(f"{subject}\n{body}")
    else:
        send_email(subject, body)
