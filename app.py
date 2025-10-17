# app.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from config.logging_config import logger
from assistant.assistant import AIAssistant
from assistant.session import ConversationManager

app = Flask(__name__)

try:
    session_manager = ConversationManager()
    assistant = AIAssistant(session_manager=session_manager)
    logger.info("Successfully initialized Lola, Nikol's AI Assistant.")
except (ValueError, FileNotFoundError) as e:
    logger.critical(f"Application failed to initialize: {e}")
    assistant = None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    if not assistant:
        return "Application not initialized.", 500

    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', None)

    logger.info(
        f"Incoming message from {sender_number} | Media: {'Yes' if media_url else 'No'} | Body: '{incoming_msg}'"
    )

    # The assistant now returns a list of messages to send
    list_of_messages = assistant.get_response(sender_number, incoming_msg, media_url)

    # --- Build TwiML response with multiple messages ---
    response = MessagingResponse()
    for message_content in list_of_messages:
        if message_content: # Ensure we don't send empty messages
            response.message(message_content)
    
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)