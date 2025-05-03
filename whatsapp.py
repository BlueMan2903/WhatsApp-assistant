from twilio.rest import Client
from secret import account_sid, auth_token

MY_PERSONAL_WHATSAPP_NUMBER = 'whatsapp:+972547958073' 
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886' 

client = Client(account_sid, auth_token)

def send_msg(text):
    client.messages.create(
        from_ = TWILIO_WHATSAPP_NUMBER,
        body = text,
        to = MY_PERSONAL_WHATSAPP_NUMBER
    )