# app.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from config.logging_config import logger
from assistant.assistant import AIAssistant
from assistant.session import ConversationManager
from twilio_whatsapp import send_handoff_message_to_nikol
import config.config as config
import json

app = Flask(__name__)

try:
    session_manager = ConversationManager()
    assistant = AIAssistant(session_manager=session_manager)

    with open("contexts/assistant_assets.json", 'r', encoding='utf-8') as f:
        assets = json.load(f)
    HANDOFF_MESSAGE_HE = assets["handoff_message_he"]

    logger.info("Successfully initialized Lola, Nikol's AI Assistant.")
except (ValueError, FileNotFoundError) as e:
    logger.critical(f"Application failed to initialize: {e}")
    assistant = None
    HANDOFF_MESSAGE_HE = "אנו כרגע חווים תקלה טכנית. ניקול תיצור איתך קשר בקרוב"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    if not assistant:
        return "Application not initialized.", 500

    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', None)

    logger.info(
        f"Incoming message from {sender_number} | Media: {'Yes' if media_url else 'No'} | Body: '{incoming_msg[::-1]}'"
    )

    try:
        response = MessagingResponse()

        # The assistant now returns a list of messages to send
        list_of_messages = assistant.get_response(sender_number, incoming_msg, media_url)

        # --- Build TwiML response with multiple messages ---
        response = MessagingResponse()
        for message_content in list_of_messages:
            if message_content: # Ensure we don't send empty messages
                response.message(message_content)
                logger.info(f"Outgoing message to {sender_number} | Body: '{message_content[::-1]}'")
        
        return str(response)
    
    except Exception as e:
        # This is the global safety net. Catches errors from assistant.py
        logger.error(f"FATAL ASSISTANT ERROR for {sender_number}: {e}", exc_info=True)

        # Plan 1: Send handoff to Nikol on failure
        try:
            history_string = session_manager.get_formatted_history(sender_number)
            error_message = f"--- CONVERSATION FAILED ---\nError: {e}\n\n{history_string}"
            
            send_handoff_message_to_nikol(
                customer_phone=sender_number,
                customer_name="Failed Session",
                query=error_message,
                image_url=media_url # Send the image if it was part of the failing message
            )
        except Exception as handoff_e:
            # Log if the handoff itself fails, so we know about it
            logger.error(f"FATAL HANDOFF ERROR for {sender_number}: {handoff_e}", exc_info=True)

        # Send the standard handoff message to the user
        response.message(HANDOFF_MESSAGE_HE)
        return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)