# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from config.logging_config import logger
from assistant.assistant import AIAssistant
from assistant.session import ConversationManager
import config.config as config
import json
from email_notifier import send_error_email

app = Flask(__name__)
CORS(app)

try:
    session_manager = ConversationManager()
    assistant = AIAssistant(session_manager=session_manager)

    with open("contexts/assistant_assets.json", 'r', encoding='utf-8') as f:
        assets = json.load(f)
    HANDOFF_MESSAGE_HE = assets["handoff_message_he"]

    logger.info("Successfully initialized Lola, Nikol's AI Assistant for Web Chat.")
except (ValueError, FileNotFoundError) as e:
    logger.critical(f"Application failed to initialize: {e}")
    assistant = None
    HANDOFF_MESSAGE_HE = "אנו כרגע חווים תקלה טכנית. ניקול תיצור איתך קשר בקרוב"


@app.route("/chat", methods=['POST'])
def chat_api():
    if not assistant:
        return jsonify({"error": "Application not initialized."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400

    sender_id = data.get('sender_id')
    incoming_msg = data.get('message', '').strip()
    image_data_url = data.get('image', None)
    
    if not sender_id:
        return jsonify({"error": "sender_id is required."}), 400

    logger.info(
        f"Incoming message from {sender_id} | Media: {'Yes' if image_data_url else 'No'} | Body: '{incoming_msg}'"
    )

    try:
        list_of_messages = assistant.get_response(sender_id, incoming_msg, image_data_url)
        full_response = "\n".join(filter(None, list_of_messages))
        logger.info(f"Outgoing message to {sender_id} | Body: '{full_response}'")
        return jsonify({"response": full_response})
    
    except Exception as e:
        logger.error(f"FATAL ASSISTANT ERROR for {sender_id}: {e}", exc_info=True)
        try:
            subject = f"CRITICAL ERROR: Assistant Crash ({sender_id})"
            body = f"User: {sender_id}\nLast Message: {incoming_msg}\n\nError: {str(e)}"
            send_error_email(subject, body)
        except Exception as email_e:
            logger.error(f"Failed to send error email: {email_e}")
        error_message = "I'm sorry, I seem to be having a technical issue. Please try again in a moment."
        return jsonify({"response": error_message}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)