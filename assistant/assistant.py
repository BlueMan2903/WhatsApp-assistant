import json
import config.config as config
import re
from config.logging_config import logger
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .session import ConversationManager
from email_notifier import send_error_email

class AIAssistant:
    def __init__(self, session_manager: ConversationManager):
        if not config.MODEL_CONFIG["google_api_key"]:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.session_manager = session_manager
        self.system_message_content = self._load_system_message()
        self.llm = init_chat_model(model=config.MODEL, **config.MODEL_CONFIG)
        with open("contexts/assistant_assets.json", 'r', encoding='utf-8') as f:
            self.assets = json.load(f)

    def _load_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_system_message(self) -> str:
        intro = self._load_file("contexts/prompt.txt")
        rules = self._load_file("contexts/rules.txt")
        with open("contexts/assistant_assets.json", 'r', encoding='utf-8') as f:
            data = json.dumps(json.load(f), ensure_ascii=False)
        return f"{intro}\n{rules}\n\n<clinic_data>\n{data}\n</clinic_data>"

    def get_response(self, sender_id: str, user_message: str, image_url: str = None) -> list[str]:
        if config.RESET_CHAT_ENABLED and user_message.strip().lower() == "/reset":
            system_message = SystemMessage(content=self.system_message_content)
            self.session_manager.reset_session(sender_id, system_message)
            return ["The chat has been reset."]

        try:
            session = self.session_manager.get_session(sender_id)
            if not session:
                system_message = SystemMessage(content=self.system_message_content)
                session = self.session_manager.start_new_session(sender_id, system_message)
            
            history = session['history']

            # --- DATABASE-AWARE CONTEXT INJECTION ---
            # Give the AI its "long-term memory" before it thinks.
            user_name = self.session_manager.get_data(sender_id, 'user_name')
            identity_context = f"SYSTEM IDENTITY DATA: Name: {user_name if user_name else 'Unknown'}"
            
            # Clean up old identity hints and inject the latest one
            history = [msg for msg in history if not (isinstance(msg, SystemMessage) and "SYSTEM IDENTITY DATA:" in msg.content)]
            history.insert(1, SystemMessage(content=identity_context))

            # --- AI-DRIVEN FLOW (NO PYTHON INTERCEPTION) ---
            content_parts = []
            if user_message: content_parts.append({"type": "text", "text": user_message})
            if image_url:
                try:
                    base64_image = image_url.split(",")[1]
                    content_parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                except: return ["אני מצטערת, הייתה בעיה בעיבוד התמונה."]
            
            if not content_parts: return ["לא התקבלה הודעה."]
            history.append(HumanMessage(content=content_parts))
        
            model_response = self.llm.invoke(history)
            ai_content = model_response.content
            if isinstance(ai_content, list): ai_content = "".join([str(item) for item in ai_content])
            history.append(AIMessage(content=ai_content))

            # --- PURGE & SAVE ---
            scrubbed_history = []
            for msg in history:
                if isinstance(msg, HumanMessage) and isinstance(msg.content, list):
                    new_c = [{"type": "text", "text": p['text']} if p['type'] == 'text' else {"type": "text", "text": "[Image Purged]"} for p in msg.content]
                    scrubbed_history.append(HumanMessage(content=new_c))
                else: scrubbed_history.append(msg)
            self.session_manager.save_history(sender_id, scrubbed_history, session.get('state'))

            # --- SIMPLE ACTION PARSING ---
            messages_to_send = []
            
            # Look for a SAVE_NAME tag first
            save_name_match = re.search(r'\[ACTION: SAVE_NAME: (.*?)\]', ai_content)
            if save_name_match:
                name_to_save = save_name_match.group(1).strip()
                if name_to_save:
                    self.session_manager.update_data(sender_id, 'user_name', name_to_save)

            # Clean all tags from the response before sending
            clean_response = re.sub(r'\[ACTION:.*?\]', '', ai_content).strip()
            if clean_response: messages_to_send.append(clean_response)

            # Handle other simple actions
            other_actions = re.findall(r'\[ACTION: (\w+)\]', ai_content)
            for action in other_actions:
                if action == "SEND_PRICE_MENU":
                    if not self.session_manager.get_data(sender_id, 'price_menu_sent'):
                        self.session_manager.update_data(sender_id, 'price_menu_sent', True)
                        messages_to_send.append("<img src='/static/nikol-price-menu.jpeg?v=1' class='chat-image-insert' />")
                elif action == "PROVIDE_BOOKING_LINK":
                    messages_to_send.append(f"ניתן לקבוע תור בקישור הבא:\n{config.BOOKING_URL}?ref={sender_id}")
                elif action == "REFER_TO_DIABETES_CLINIC":
                     messages_to_send.append(self.assets.get("diabetes_referral_he", "אנו ממליצים לפנות למרפאת סוכרת."))

            return messages_to_send

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return ["אני מצטערת, יש כרגע תקלה. ניקול תיצור איתך קשר בהקדם."]

    # The _finalize_handoff and _execute_standard_action methods are no longer needed in this flow
    # but can be kept for future features. For now, they are not called.