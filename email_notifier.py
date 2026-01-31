import resend
import config.config as config
from config.logging_config import logger

def _send_email_base(subject: str, body: str, log_context: str):
    """
    Sends an email using Resend.
    """
    if not config.RESEND_API_KEY:
        logger.error(f"{log_context}: Missing RESEND_API_KEY in .env")
        return

    resend.api_key = config.RESEND_API_KEY

    # FOR TESTING: Use 'onboarding@resend.dev' as the sender.
    # It only allows sending emails TO the email address you signed up with.
    # Once you verify a domain (e.g., nikol.clinic), you can change 'from' to 'Lola <info@nikol.clinic>'
    
    from_email = "Lola <onboarding@resend.dev>"
    
    params = {
        "from": from_email,
        "to": [config.NIKOL_EMAIL_ADDRESS],
        "subject": subject,
        "text": body,
    }

    try:
        email = resend.Emails.send(params)
        # Resend returns an object, we check if 'id' exists
        if hasattr(email, 'id'): 
             logger.info(f"{log_context} Email sent successfully! ID: {email.id}")
        else:
             # Sometimes it returns a dict depending on version
             logger.info(f"{log_context} Email sent successfully! Response: {email}")

    except Exception as e:
        logger.error(f"{log_context} FATAL ERROR: Failed to send via Resend: {e}", exc_info=True)

def send_error_email(subject: str, body: str):
    _send_email_base(subject, body, "HANDOFF/ERROR")

def send_startup_email():
    _send_email_base("System Alert: Lola Initialized", "Lola is online and ready.", "SYSTEM STARTUP")