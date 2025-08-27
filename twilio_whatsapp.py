import os
import config.config as config
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from time import sleep
from config.logging_config import logger
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if not ACCOUNT_SID or not AUTH_TOKEN:
    logger.warning("WARNING: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN environment variables are not set.")
    logger.warning("WhatsApp messages will not be sent/received correctly without these credentials.")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Retry on any exception EXCEPT a TwilioRestException with status 429
def is_not_rate_limit_error(exception):
    return not (isinstance(exception, TwilioRestException) and exception.status == 429)

@retry(stop=stop_after_attempt(config.MAX_RETRIES), wait=wait_fixed(config.RETRY_DELAY), retry=retry_if_exception(is_not_rate_limit_error))
def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using Twilio.
    :param to_number: The recipient's WhatsApp number (e.g., 'whatsapp:+1234567890')
    :param message_body: The content of the message
    :return: Twilio Message instance
    """
    if config.DELAY:
        delay = len(message_body) / 3
    else:
        delay = 0

    try:
        sleep(delay)
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message_body,
            to=to_number
        )
        logger.info(f"Message sent successfully! SID: {message.sid}")
        logger.info(f"Sending response to {to_number} | Body: '{message_body}'")
        return message
    except TwilioRestException as e:
        if e.status == 429:
            logger.critical(e)
            # Do not re-raise, so tenacity does not retry. Return None to signal failure.
            return None
        else:
            # For other Twilio errors (e.g., invalid number), log and re-raise for tenacity
            logger.error(f"Twilio REST Error sending to {to_number}: {e}")
            raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        logger.error(f"Message body: {message_body}")
        logger.error(f"Error sending message to {to_number}: {e}")
        raise
    
# NEW FUNCTION
def send_handoff_message_to_nikol(customer_phone: str, customer_name: str, query: str, image_url: str = None):
    """Sends a formatted handoff message to Nikol."""
    if not config.NIKOL_WHATSAPP_NUMBER:
        logger.error("ERROR: NIKOL_WHATSAPP_NUMBER is not set. Cannot send handoff message.")
        return
    
    body = f"היי ניקול, יש פנייה חדשה:\n\n"
    body += f"שם: {customer_name}\n"
    body += f"טלפון: {customer_phone}\n"
    body += f"פנייה: {query}\n"
    
    if image_url:
        body += f"תמונה: {image_url}"
    send_whatsapp_message(config.NIKOL_WHATSAPP_NUMBER, body)