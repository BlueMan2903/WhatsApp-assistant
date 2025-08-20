import base64
import requests
import json
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import config
from .session import ConversationManager

class AIAssistant:
    """The AI assistant specifically for the Podiatrist Clinic."""

    def __init__(self, session_manager: ConversationManager):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        self.session_manager = session_manager
        self.system_message_content = self._load_system_message()
        self.llm = init_chat_model(
            "gemini-2.5-flash",
            model_provider="google_genai",
            google_api_key=config.GEMINI_API_KEY
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
        """Gets an AI response for a given user, message, and optional image."""
        history = self.session_manager.get_history(sender_id)
        if not history:
            system_message = SystemMessage(content=self.system_message_content)
            history = self.session_manager.start_new_session(sender_id, system_message)

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

        try:
            history.append(HumanMessage(content=content_parts))
            model_resp = self.llm.invoke(history)
            history.append(AIMessage(content=model_resp.content))
            return model_resp.content
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            return "מצטער, אני נתקל בבעיה טכנית. אנא נסה שוב בעוד מספר רגעים."