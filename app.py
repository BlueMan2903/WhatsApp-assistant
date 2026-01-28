# app.py
from flask import Flask, request, jsonify ### MODIFIED: Import jsonify for API responses
from flask_cors import CORS ### NEW: Import CORS for cross-origin requests
from email_notifier import send_startup_email, send_error_email
from config.logging_config import logger
from assistant.assistant import AIAssistant
from assistant.session import ConversationManager
import config.config as config
import json

app = Flask(__name__)
### NEW: Enable CORS to allow your frontend to make requests to this backend
CORS(app)

try:
    session_manager = ConversationManager()
    assistant = AIAssistant(session_manager=session_manager)

    with open("contexts/assistant_assets.json", 'r', encoding='utf-8') as f:
        assets = json.load(f)
    # This can still be used for a generic error message
    HANDOFF_MESSAGE_HE = assets["handoff_message_he"]

    logger.info("Successfully initialized Lola, Nikol's AI Assistant for Web Chat.")
    send_startup_email()

except (ValueError, FileNotFoundError) as e:
    logger.critical(f"Application failed to initialize: {e}")
    assistant = None
    HANDOFF_MESSAGE_HE = "אנו כרגע חווים תקלה טכנית. ניקול תיצור איתך קשר בקרוב"


@app.route("/chat", methods=['POST'])
def chat_api():
    if not assistant:
        return jsonify({"error": "Application not initialized."}), 500

    ### MODIFIED: Get data from the JSON body of the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400

    sender_id = data.get('sender_id')
    incoming_msg = data.get('message', '').strip()
    # The frontend now sends a base64 data URL directly
    image_data_url = data.get('image', None)
    
    if not sender_id:
        return jsonify({"error": "sender_id is required."}), 400

    logger.info(
        f"Incoming message from {sender_id} | Media: {'Yes' if image_data_url else 'No'} | Body: '{incoming_msg[::-1]}'"
    )

    try:
        # The assistant returns a list of messages
        list_of_messages = assistant.get_response(sender_id, incoming_msg, image_data_url)

        # Join the messages into a single string for the JSON response
        full_response = "\n".join(filter(None, list_of_messages))
        
        logger.info(f"Outgoing message to {sender_id} | Body: '{full_response[::-1]}'")

        ### MODIFIED: Send the response back as JSON
        return jsonify({"response": full_response})
    
    except Exception as e:
        # This is the global safety net
        logger.error(f"FATAL ASSISTANT ERROR for {sender_id}: {e}", exc_info=True)

        try:
            email_subject = f"CRITICAL ERROR: Lola Web Chat ({sender_id})"
            email_body = (
                f"A fatal error occurred during a chat session.\n\n"
                f"User ID: {sender_id}\n"
                f"Error Message: {str(e)}\n\n"
                f"Please check the server logs for the full traceback."
            )
            send_error_email(email_subject, email_body)
        except Exception as email_err:
            logger.error(f"Failed to send crash notification email: {email_err}")

        # Send a user-friendly error message back to the frontend
        error_message = "אני מצטערת, יש כרגע תקלה במערבת. תוכלי להמתין דקה?"
        return jsonify({"response": error_message}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)