from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, SMS_TO_NUMBER


def send_sms(body: str):
    if not TWILIO_ACCOUNT_SID:
        print("[SMS] TWILIO_ACCOUNT_SID not set. Skipping.")
        return

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_FROM_NUMBER,
            to=SMS_TO_NUMBER,
        )
        print(f"[SMS] Sent — SID: {message.sid}")
    except Exception as e:
        print(f"[SMS] Failed to send: {e}")
