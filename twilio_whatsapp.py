import os
import config
from twilio.rest import Client

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if not ACCOUNT_SID or not AUTH_TOKEN:
    print("WARNING: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN environment variables are not set.")
    print("WhatsApp messages will not be sent/received correctly without these credentials.")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using Twilio.
    :param to_number: The recipient's WhatsApp number (e.g., 'whatsapp:+1234567890')
    :param message_body: The content of the message
    :return: Twilio Message instance
    """
    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message_body,
            to=to_number
        )
        print(f"Message sent successfully! SID: {message.sid}")
        return message
    except Exception as e:
        print(f"Error sending message: {e}")
        return None
    
# NEW FUNCTION
def send_handoff_message_to_nikol(customer_phone: str, customer_name: str, query: str, image_url: str = None):
    """Sends a formatted handoff message to Nikol."""
    if not config.NIKOL_WHATSAPP_NUMBER:
        print("ERROR: NIKOL_WHATSAPP_NUMBER is not set. Cannot send handoff message.")
        return

    body = f"היי ניקול, יש פנייה חדשה:\n\n"
    body += f"שם: {customer_name}\n"
    body += f"טלפון: {customer_phone}\n"
    body += f"פנייה: {query}\n"
    if image_url:
        body += f"תמונה: {image_url}"

    send_whatsapp_message(config.NIKOL_WHATSAPP_NUMBER, body)