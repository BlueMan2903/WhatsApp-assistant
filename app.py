# app.py
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from assistant.assistant import AIAssistant
from assistant.session import ConversationManager
from twilio_whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('whatsapp_messages.log', maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # Simplified formatter
handler.setFormatter(formatter)
logger.addHandler(handler)


app = Flask(__name__)

try:
    session_manager = ConversationManager()
    assistant = AIAssistant(session_manager=session_manager)
    print("Successfully initialized Lola, Nikol's AI Assistant.")
except (ValueError, FileNotFoundError) as e:
    print(f"ERROR starting application: {e}")
    logger.critical(f"Application failed to initialize: {e}")
    assistant = None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    if not assistant:
        return "Application not initialized due to configuration error.", 500

    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', None)

    logger.info(
        f"Incoming message from {sender_number} | Media: {'Yes' if media_url else 'No'} | Body: '{incoming_msg}'"
    )

    ai_response_content = assistant.get_response(sender_number, incoming_msg, media_url)

    send_whatsapp_message(sender_number, ai_response_content)
    
    return str(MessagingResponse())

if __name__ == "__main__":
    app.run(debug=True, port=5000)