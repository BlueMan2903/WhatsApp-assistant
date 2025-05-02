from twilio.rest import Client
from secret import account_sid, auth_token

client = Client(account_sid, auth_token)

def send_msg(text):
    client.messages.create(
        from_ = 'whatsapp:+14155238886',
        body = text,
        to = 'whatsapp:+972547958073'
    )