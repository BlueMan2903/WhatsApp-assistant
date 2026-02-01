# config.py
import os

# Gemini config
MODEL = "gemini-2.5-flash"
# MODEL = "gemini-3-flash-preview"
MODEL_CONFIG = {
    "model_provider": "google_genai",
    "google_api_key": os.getenv("GEMINI_API_KEY")
}

ENVIRONMENT = os.getenv("ENVIRONMENT", "testing")
if ENVIRONMENT == "production":
    # The specific URL you requested for production
    CHAT_API_URL = "https://stirring-yearly-anteater.ngrok-free.app/chat"
else:
    # Relative path for local/testing (avoids CORS and network issues)
    CHAT_API_URL = "/chat"

NGROK_SETUP = "ngrok config add-authtoken 31btVlpGpJvGNMgMuVoDhie3nhS_2XL9vKr9Dsyu3hoQP5hfq"
NGROK_COMMAND = "ngrok http --url=stirring-yearly-anteater.ngrok-free.app 5000"

BOOKING_URL = os.getenv("BOOKING_URL")

# Enable delay for simulating human response time
DELAY = False

# Retry config for sending whatsapp message
MAX_RETRIES = 5
# delay in seconds
RETRY_DELAY = 10

RESET_CHAT_ENABLED = True

# --- NEW: Email Notifier Configuration (MailerSend) ---
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
MAILERSEND_API_TOKEN = os.getenv("MAILERSEND_API_TOKEN")
# This is the "From" email you verified with MailerSend
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# This is the email address you want to send alerts TO
NIKOL_EMAIL_ADDRESS = os.getenv("NIKOL_EMAIL_ADDRESS")