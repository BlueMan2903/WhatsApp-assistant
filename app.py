# app.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from assistant.assistant import AIAssistant
from assistant.session import ConversationManager
from twilio_whatsapp import send_whatsapp_message

app = Flask(__name__)

try:
    session_manager = ConversationManager()
    assistant = AIAssistant(session_manager=session_manager)
    print("Successfully initialized the Podiatrist AI Assistant.")
except (ValueError, FileNotFoundError) as e:
    print(f"ERROR starting application: {e}")
    assistant = None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    if not assistant:
        return "Application not initialized due to configuration error.", 500

    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', None)

    ai_response_content = assistant.get_response(sender_number, incoming_msg, media_url)

    send_whatsapp_message(sender_number, ai_response_content)
    
    return str(MessagingResponse())

if __name__ == "__main__":
    app.run(debug=True, port=5000)