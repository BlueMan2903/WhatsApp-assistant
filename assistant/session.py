# assistant/session.py
from langchain_core.messages import SystemMessage

class ConversationManager:
    """Manages conversation sessions for multiple users."""
    def __init__(self):
        self._sessions = {}

    def get_history(self, session_id: str):
        return self._sessions.get(session_id)

    def start_new_session(self, session_id: str, system_message: SystemMessage):
        """Creates a new conversation history initialized with a system message."""
        self._sessions[session_id] = [system_message]
        return self._sessions[session_id]