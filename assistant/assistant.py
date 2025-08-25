import base64
import requests
import json
import config.config as config
import re
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .session import ConversationManager
from twilio_whatsapp import send_handoff_message_to_nikol

class AIAssistant:
    """The AI assistant specifically for the Podiatrist Clinic."""

    def __init__(self, session_manager: ConversationManager):
        if not config.MODEL_CONFIG["google_api_key"]:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        self.session_manager = session_manager
        self.system_message_content = self._load_system_message()
        self.llm = init_chat_model(
            model=config.MODEL,
            **config.MODEL_CONFIG
        )

    def _load_file(self, path):
        """Helper to load a text file."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_system_message(self) -> str:
        """Loads and combines the podiatrist persona files into a single system prompt."""
        intro = self._load_file("contexts/prompt.txt")
        rules = self._load_file("contexts/rules.txt")
        with open("contexts/treatments.json", 'r', encoding='utf-8') as f:
            data = json.dumps(json.load(f), ensure_ascii=False)
        
        return f"{intro}\n{rules}\n{data}"

    def _get_image_base64(self, image_url: str) -> str | None:
        """Fetches an image from a Twilio URL and returns it as a base64 string."""
        try:
            response = requests.get(
                image_url,
                auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            )
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image from Twilio: {e}")
            return None

    def get_response(self, sender_id: str, user_message: str, image_url: str = None) -> str:
        session = self.session_manager.get_session(sender_id)
        if not session:
            system_message = SystemMessage(content=self.system_message_content)
            session = self.session_manager.start_new_session(sender_id, system_message)
        
        history = session['history']
        
        # --- Add new message to history ---
        content_parts = []
        if user_message:
            content_parts.append({"type": "text", "text": user_message})
        if image_url:
            base64_image = self._get_image_base64(image_url)
            if base64_image:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
            else:
                return "אני מצטער, לא הצלחתי לעבד את התמונה ששלחת. אנא נסה שוב."
        
        if not content_parts:
            return "No message received."
            
        history.append(HumanMessage(content=content_parts))
        
        # --- Get LLM response and parse for actions ---
        try:
            model_response = self.llm.invoke(history)
            ai_content = model_response.content
            history.append(AIMessage(content=ai_content))

            # Use regex to find an action tag like [ACTION: DO_SOMETHING]
            action_match = re.search(r'\[ACTION:\s*(\w+)\s*\]', ai_content)
            
            clean_response = re.sub(r'\[ACTION:\s*\w+\s*\]', '', ai_content).strip()

            if action_match:
                action = action_match.group(1)
                self._execute_action(action, sender_id, user_message, image_url)
            
            return clean_response

        except Exception as e:
            print(f"Error invoking LLM or executing action: {e}")
            return "מצטער, אני נתקל בבעיה טכנית. אנא נסה שוב בעוד מספר רגעים."

    def _execute_action(self, action: str, sender_id: str, user_message: str, image_url: str):
        """Executes actions based on the parsed tag from the LLM response."""
        print(f"Executing action '{action}' for user {sender_id}")
        if action == "FORWARD_TO_NIKOL":
            # For the MVP, we'll use the user's message as their name for now.
            # A future step would be to explicitly ask for their name.
            customer_name = user_message.split()[0] if user_message else "לא צוין שם"
            send_handoff_message_to_nikol(
                customer_phone=sender_id,
                customer_name=customer_name,
                query=user_message,
                image_url=image_url
            )
        elif action == "PROVIDE_BOOKING_LINK":
            # The main response already contains the booking text, so we just append the link.
            booking_message = f"ניתן לקבוע תור דרך הקישור הבא:\n{config.BOOKING_URL}"
            # This needs to be sent as a separate message via Twilio.
            from twilio_whatsapp import send_whatsapp_message
            send_whatsapp_message(sender_id, booking_message)