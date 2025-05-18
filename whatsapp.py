from twilio.rest import Client
from os import environ

RECIPIENT_WHATSAPP_NUMBERS = 'whatsapp:+972547958073'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886' 

try:
    account_sid = environ["TWILIO_ACCOUNT_SID"]
    auth_token = environ["TWILIO_AUTH_TOKEN"]
except KeyError as e:
    print(f"Error: Environment variable {e} not set.")
    print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
    exit(1)

client = Client(account_sid, auth_token)

def send_msg(text, number):
    client.messages.create(
        from_ = TWILIO_WHATSAPP_NUMBER,
        body = text,
        to = number
    )