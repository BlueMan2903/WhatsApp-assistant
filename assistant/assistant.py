# assistant.py

import base64
import requests
import json
import config.config as config
import re
from config.logging_config import logger
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .session import ConversationManager
from email_notifier import send_error_email # ### NEW: Import the email handoff function

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
        with open("contexts/assistant_assets.json", 'r', encoding='utf-8') as f:
            data = json.dumps(json.load(f), ensure_ascii=False)
        
        return f"{intro}\n{rules}\n{data}"

    ### MODIFIED: This method is now OBSOLETE as the frontend sends base64 directly.
    # It's no longer called in the main workflow.
    def _get_image_base64(self, image_url: str) -> str | None:
        """Fetches an image from a Twilio URL and returns it as a base64 string."""
        logger.warning("DEPRECATED: _get_image_base64 should no longer be called.")
        try:
            response = requests.get(
                image_url,
                auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            )
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching image from Twilio: {e}")
            raise Exception(f"Twilio image download failed: {e}")

    def get_response(self, sender_id: str, user_message: str, image_url: str = None) -> list[str]:
        """
        Processes user input and returns a list of messages to be sent in order.
        """
        if config.RESET_CHAT_ENABLED and user_message.strip().lower() == "/reset":
            system_message = SystemMessage(content=self.system_message_content)
            self.session_manager.reset_session(sender_id, system_message)
            logger.info(f"Conversation reset for user {sender_id}")
            return ["The chat has been reset."]

        try:
            session = self.session_manager.get_session(sender_id)
            if not session:
                system_message = SystemMessage(content=self.system_message_content)
                session = self.session_manager.start_new_session(sender_id, system_message)
            
            history = session['history']
            
            # --- Add new message to history ---
            content_parts = []
            if user_message:
                content_parts.append({"type": "text", "text": user_message})
            
            ### MODIFIED: This section now handles the base64 data URL directly.
            if image_url:
                try:
                    # A data URL looks like "data:image/jpeg;base64,iVBORw0KGgo..."
                    # We just need the part after the comma.
                    base64_image = image_url.split(",")[1]
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })
                except (IndexError, AttributeError):
                    logger.error(f"Malformed base64 data URL for user {sender_id}")
                    return ["אני מצטער, הייתה בעיה בעיבוד התמונה ששלחת. אנא נסה שוב."]
            
            if not content_parts:
                return ["לא התקבלה הודעה."]
                
            history.append(HumanMessage(content=content_parts))
        
            # --- Get LLM response and parse for actions ---
            model_response = self.llm.invoke(history)
            ai_content = model_response.content
            history.append(AIMessage(content=ai_content))

            messages_to_send = []
            
            clean_response = re.sub(r'\[ACTION:\s*\w+\s*\]', '', ai_content).strip()
            if clean_response:
                messages_to_send.append(clean_response)

            action_match = re.search(r'\[ACTION:\s*(\w+)\s*\]', ai_content)
            if action_match:
                action = action_match.group(1)
                follow_up_message = self._execute_action(action, sender_id, user_message, image_url)
                if follow_up_message:
                    messages_to_send.append(follow_up_message)
            
            return messages_to_send

        except Exception as e:
            logger.error(f"Error in get_response for {sender_id}: {e}")
            raise Exception(f"Assistant failure: {e}")

    def _execute_action(self, action: str, sender_id: str, user_message: str, image_url: str) -> str | None:
        """
        Executes background tasks and returns content for any follow-up messages.
        """
        logger.info(f"Executing action '{action}' for user {sender_id}")
        if action == "FORWARD_TO_NIKOL":
            logger.info(f"HANDOFF ACTION TRIGGERED for user {sender_id}")
            logger.info(f"Customer Query: {user_message}")
            if image_url:
                logger.info("An image was included in the handoff.")

            # --- NEW: Send email handoff for NORMAL operations ---
            try:
                # We use self.session_manager here, which is available to the class
                history_string = self.session_manager.get_formatted_history(sender_id)
                
                subject = f"Lola AI Bot - Handoff Request - User: {sender_id}"
                body = (
                    f"The AI has requested a human handoff for the user.\n\n"
                    f"User: {sender_id}\n"
                    f"Last Message: {user_message}\n"
                    f"Image Sent: {'Yes' if image_url else 'No'}\n\n"
                    f"--- CONVERSATION HISTORY ---\n"
                    f"{history_string}"
                )
                
                # Call the email notifier function
                send_error_email(subject, body)

            except Exception as e:
                logger.error(f"Failed to send NORMAL handoff email: {e}")
            
            return None # No follow-up message for the user

        elif action == "PROVIDE_BOOKING_LINK":
            return f"ניתן לקבוע תור דרך הקישור הבא:\n{config.BOOKING_URL}"
        
        return None