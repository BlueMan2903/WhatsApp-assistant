import config.config as config
from config.logging_config import logger
from mailersend import MailerSendClient, EmailBuilder

def send_error_email(subject: str, body: str):
    """
    Sends an error notification email using the MailerSend API.
    """
    
    # Check if MailerSend configuration is missing
    if not all([config.MAILERSEND_API_TOKEN, config.SENDER_EMAIL, config.NIKOL_EMAIL_ADDRESS]):
        logger.error("EMAIL HANDOFF FAILED: Missing MAILERSEND_API_TOKEN, SENDER_EMAIL, or NIKOL_EMAIL_ADDRESS in .env")
        return

    logger.info(f"Attempting to send error email via MailerSend to {config.NIKOL_EMAIL_ADDRESS}...")

    try:
        # 1. Initialize the MailerSend client
        ms = MailerSendClient(config.MAILERSEND_API_TOKEN)

        # 2. Define the email parameters
        email_params = (EmailBuilder()
                        .from_email(config.SENDER_EMAIL, "Lola AI Bot")
                        .to_many([{"email": config.NIKOL_EMAIL_ADDRESS, "name": "Nikol"}])
                        .subject(subject)
                        .text(body)
                        .build())

        # 3. Send the email
        response = ms.emails.send(email_params)
        
        if 200 <= response.status_code < 300:
             logger.info(f"Email handoff sent successfully! Status code: {response.status_code}")
        else:
            logger.error(f"FATAL EMAIL HANDOFF ERROR: MailerSend returned status {response.status_code}")
            logger.error(f"Response: {response.text}")

    except Exception as e:
        logger.error(f"FATAL EMAIL HANDOFF ERROR: Failed to send email via MailerSend: {e}", exc_info=True)