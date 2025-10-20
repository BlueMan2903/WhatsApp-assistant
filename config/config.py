# config.py
import os

# Gemini config
MODEL = "gemini-2.5-flash"
MODEL_CONFIG = {
    "model_provider": "google_genai",
    "google_api_key": os.getenv("GEMINI_API_KEY")
}

# OpenAI config
# MODEL = "gpt-5-mini"  
# MODEL_CONFIG = {
#     "model_provider": "openai",
#     "openai_api_key": os.getenv("OPENAI_API_KEY")
# }

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

NGROK_SETUP = "ngrok config add-authtoken 31btVlpGpJvGNMgMuVoDhie3nhS_2XL9vKr9Dsyu3hoQP5hfq"
NGROK_COMMAND = "ngrok http --url=stirring-yearly-anteater.ngrok-free.app 5000"

# New configuration for MVP actions
NIKOL_WHATSAPP_NUMBER = os.getenv("NIKOL_WHATSAPP_NUMBER")
BOOKING_URL = os.getenv("BOOKING_URL")

# Enable delay for simulating human response time
DELAY = False

# Retry config for sending whatsapp message
MAX_RETRIES = 5
# delay in seconds
RETRY_DELAY = 10

RESET_CHAT_ENABLED = True