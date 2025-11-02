# app.py
from flask import Flask, request, jsonify ### MODIFIED: Import jsonify for API responses
from flask_cors import CORS ### NEW: Import CORS for cross-origin requests
from config.logging_config import logger
from assistant.assistant import AIAssistant
from assistant.session import ConversationManager
# ### REMOVED: No longer need Twilio handoff in the main app file
# from twilio_whatsapp import send_handoff_message_to_nikol
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
except (ValueError, FileNotFoundError) as e:
    logger.critical(f"Application failed to initialize: {e}")
    assistant = None
    HANDOFF_MESSAGE_HE = "אנו כרגע חווים תקלה טכנית. ניקול תיצור איתך קשר בקרוב"


### MODIFIED: This is the new API endpoint for the web chat
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

        ### MODIFIED: The handoff to Nikol via Twilio is removed.
        # We now log the error and send a generic error message to the user.
        # A future improvement could be to send an email notification here.
        
        # Send a user-friendly error message back to the frontend
        error_message = "I'm sorry, I seem to be having a technical issue. Please try again in a moment."
        return jsonify({"response": error_message}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)