import os

# --- Gemini Configuration ---
# Uses the model defined in .env, or defaults to 2.5-flash if missing
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

MODEL_CONFIG = {
    "model_provider": "google_genai",
    "google_api_key": os.getenv("GEMINI_API_KEY")
}

# (Optional) Reference command, logic doesn't use this directly but good for docs
NGROK_COMMAND = "ngrok http --url=stirring-yearly-anteater.ngrok-free.app 5000"

# --- Booking ---
BOOKING_URL = os.getenv("BOOKING_URL")

# --- Dynamic Logic Settings (Loaded from .env) ---
# .env values are strings, so we must convert them to Booleans/Integers

# "False" string -> False boolean
DELAY = os.getenv("ENABLE_HUMAN_DELAY", "False").lower() == "true"

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 5))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 10))

RESET_CHAT_ENABLED = os.getenv("RESET_CHAT_ENABLED", "True").lower() == "true"

# --- Email Configuration ---
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# Default to the testing sender if not set in .env
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev") 
NIKOL_EMAIL_ADDRESS = os.getenv("NIKOL_EMAIL_ADDRESS")