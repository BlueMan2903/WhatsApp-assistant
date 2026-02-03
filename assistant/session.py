# assistant/session.py
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

class ConversationManager:
    """Manages conversation sessions for multiple users, including state."""
    def __init__(self):
        self._sessions = {}

    def get_session(self, session_id: str):
        return self._sessions.get(session_id)

    def update_state(self, session_id: str, new_state: str):
        if session_id in self._sessions:
            self._sessions[session_id]['state'] = new_state

    # --- NEW: Methods to store Name/Phone ---
    def update_data(self, session_id: str, key: str, value: str):
        """Stores auxiliary data like name or phone number."""
        if session_id in self._sessions:
            self._sessions[session_id][key] = value

    def get_data(self, session_id: str, key: str):
        """Retrieves auxiliary data."""
        return self._sessions.get(session_id, {}).get(key)
    # ----------------------------------------

    def start_new_session(self, session_id: str, system_message: SystemMessage):
        self._sessions[session_id] = {
            'history': [system_message],
            'state': 'AWAITING_INITIAL_QUERY' 
        }
        return self._sessions[session_id]
    
    def reset_session(self, session_id: str, system_message: SystemMessage):
        if session_id in self._sessions:
            self._sessions[session_id]['history'] = [system_message]
            self._sessions[session_id]['state'] = 'AWAITING_INITIAL_QUERY'
            # Clear old user data on reset
            if 'user_name' in self._sessions[session_id]: del self._sessions[session_id]['user_name']
            if 'user_phone' in self._sessions[session_id]: del self._sessions[session_id]['user_phone']
            return True
        return False
    
    def get_formatted_history(self, session_id: str) -> str:
        # (This function remains exactly the same as your previous version)
        session = self.get_session(session_id)
        if not session:
            return "No session history found."
        history: list[BaseMessage] = session.get('history', [])
        formatted_lines = []

        for msg in history:
            if isinstance(msg, SystemMessage):
                continue 
            elif isinstance(msg, HumanMessage):
                prefix = "User:"
                if isinstance(msg.content, list):
                    text_parts = [part['text'] for part in msg.content if part['type'] == 'text']
                    text = " ".join(text_parts)
                    if any(part['type'] == 'image_url' for part in msg.content):
                        text += " [Image Attached]"
                else:
                    text = msg.content
                formatted_lines.append(f"{prefix} {text}")
            elif isinstance(msg, AIMessage):
                prefix = "Lola:"
                formatted_lines.append(f"{prefix} {msg.content}")

        return "\n".join(formatted_lines)