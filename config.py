# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# New configuration for MVP actions
NIKOL_WHATSAPP_NUMBER = os.getenv("NIKOL_WHATSAPP_NUMBER")
BOOKING_URL = os.getenv("BOOKING_URL")