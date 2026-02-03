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
        self.llm = init_chat_model(
            model=config.MODEL,
            **config.MODEL_CONFIG
        )
        
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
        return f"{intro}\n{rules}\n{data}"

    def get_response(self, sender_id: str, user_message: str, image_url: str = None) -> list[str]:
        # Handle Reset Command
        if config.RESET_CHAT_ENABLED and user_message.strip().lower() == "/reset":
            system_message = SystemMessage(content=self.system_message_content)
            self.session_manager.reset_session(sender_id, system_message)
            return ["The chat has been reset."]

        try:
            # 1. Initialize or Retrieve Session
            session = self.session_manager.get_session(sender_id)
            if not session:
                system_message = SystemMessage(content=self.system_message_content)
                session = self.session_manager.start_new_session(sender_id, system_message)
            
            history = session['history']
            current_state = session.get('state', 'AWAITING_INITIAL_QUERY')

            # --- 2. INTERCEPT: HANDLE DATA COLLECTION STATES ---
            # If we are waiting for a Name or Phone, we DO NOT call the main AI logic.
            
            if current_state == 'COLLECTING_NAME':
                # User just sent their name
                self.session_manager.update_data(sender_id, 'user_name', user_message)
                self.session_manager.update_state(sender_id, 'COLLECTING_PHONE')
                
                # Add to history manually so the transcript makes sense later
                history.append(HumanMessage(content=user_message))
                msg = "תודה. על מנת שניקול תוכל לחזור אליך, מה מספר הטלפון שלך?"
                history.append(AIMessage(content=msg))
                return [msg]

            if current_state == 'COLLECTING_PHONE':
                # User just sent their phone
                self.session_manager.update_data(sender_id, 'user_phone', user_message)
                
                history.append(HumanMessage(content=user_message))
                
                # NOW we trigger the actual email and inference
                final_msg = self._finalize_handoff(sender_id, history)
                
                self.session_manager.update_state(sender_id, 'HANDOFF_COMPLETE')
                history.append(AIMessage(content=final_msg))
                return [final_msg]

            # --- 3. NORMAL FLOW (AI ANALYSIS) ---
            
            # Prepare User Message
            content_parts = []
            if user_message:
                content_parts.append({"type": "text", "text": user_message})
            
            if image_url:
                try:
                    base64_image = image_url.split(",")[1]
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })
                except (IndexError, AttributeError):
                    return ["אני מצטער, הייתה בעיה בעיבוד התמונה. אנא נסה שוב."]
            
            if not content_parts:
                return ["לא התקבלה הודעה."]
                
            history.append(HumanMessage(content=content_parts))
        
            # Call Gemini
            model_response = self.llm.invoke(history)
            ai_content = model_response.content
            if isinstance(ai_content, list):
                ai_content = "".join([str(item) for item in ai_content])

            history.append(AIMessage(content=ai_content))

            # --- 4. ACTION PARSING ---
            messages_to_send = []
            
            # Remove the action tag from the text the user sees, but keep the text!
            clean_response = re.sub(r'\[ACTION:\s*\w+\s*\]', '', ai_content).strip()
            if clean_response:
                messages_to_send.append(clean_response)

            action_match = re.search(r'\[ACTION:\s*(\w+)\s*\]', ai_content)
            if action_match:
                action = action_match.group(1)

                # --- NEW: Smart Price Menu Logic ---
                if action == "SEND_PRICE_MENU":
                    # Only send the image if we haven't sent it in this session yet
                    if not self.session_manager.get_data(sender_id, 'price_menu_sent'):
                        self.session_manager.update_data(sender_id, 'price_menu_sent', True)
                        
                        # Append the image as a separate message bubble
                        img_html = "<img src='/static/nikol-price-menu.jpeg?v=1' class='chat-image-insert' alt='Price Menu' />"
                        messages_to_send.append(img_html)
                        
                        # Log it in history so the bot knows it sent it
                        history.append(AIMessage(content="[System: Price menu image displayed to user]"))

                # --- Standard Logic ---
                elif action == "FORWARD_TO_NIKOL":
                    self.session_manager.update_state(sender_id, 'COLLECTING_NAME')
                    follow_up = "אני רואה שזה מקרה שניקול צריכה לבחון אישית. איך קוראים לך?"
                    messages_to_send.append(follow_up)
                    history.append(AIMessage(content=follow_up))
                
                else:
                    follow_up_message = self._execute_standard_action(action)
                    if follow_up_message:
                        messages_to_send.append(follow_up_message)
            
            return messages_to_send

        except Exception as e:
            logger.error(f"Error in get_response for {sender_id}: {e}")
            raise Exception(f"Assistant failure: {e}")

    def _execute_standard_action(self, action: str) -> str | None:
        """Executes simple actions like booking links."""
        if action == "PROVIDE_BOOKING_LINK":
            return f"ניתן לקבוע תור דרך הקישור הבא:\n{config.BOOKING_URL}"
        elif action == "REFER_TO_DIABETES_CLINIC":
             return self.assets.get("diabetes_referral_he", "אנו ממליצים לפנות למרפאת סוכרת.")
        return None

    def _finalize_handoff(self, sender_id: str, history: list) -> str:
        """
        Called after Name and Phone are collected.
        1. Infers the 'Reason' from chat history using Gemini.
        2. Sends the email.
        3. Returns the final success message to user.
        """
        logger.info(f"Finalizing Handoff for {sender_id}")
        
        user_name = self.session_manager.get_data(sender_id, 'user_name')
        user_phone = self.session_manager.get_data(sender_id, 'user_phone')

        # --- INFERENCE STEP ---
        # We ask Gemini to summarize the chat specifically for Nikol
        try:
            summary_prompt = [
                SystemMessage(content="You are a medical admin assistant. Read the following chat history and summarize the patient's medical complaint in one sentence (in Hebrew or English)."),
                HumanMessage(content=str(history))
            ]
            reason_response = self.llm.invoke(summary_prompt)
            inferred_reason = reason_response.content
        except Exception as e:
            logger.error(f"Failed to infer reason: {e}")
            inferred_reason = "Could not infer reason from text."

        # --- SEND EMAIL ---
        try:
            subject = f"New Lead: {user_name} ({user_phone})"
            body = (
                f"A user has been handed off to you via the Web Chat.\n\n"
                f"Name: {user_name}\n"
                f"Phone: {user_phone}\n"
                f"Reason (AI Summary): {inferred_reason}\n\n"
                f"--- Full Transcript ---\n"
                f"{self.session_manager.get_formatted_history(sender_id)}"
            )
            send_error_email(subject, body)
            logger.info("Rich Handoff email sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send handoff email: {e}")

        # Return final message to user
        return self.assets.get("handoff_message_he", "קיבלנו את הפרטים, ניקול תיצור איתך קשר בהקדם.")