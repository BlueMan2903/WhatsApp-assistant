# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# New configuration for MVP actions
NIKOL_WHATSAPP_NUMBER = os.getenv("NIKOL_WHATSAPP_NUMBER")
BOOKING_URL = os.getenv("BOOKING_URL")

# Enable delay for simulating human response time
DELAY = False

# Retry config for sending whatsapp message
MAX_RETRIES = 5
RETRY_DELAY = 1