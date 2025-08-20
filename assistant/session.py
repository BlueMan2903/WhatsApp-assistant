# assistant/session.py
from langchain_core.messages import SystemMessage

class ConversationManager:
    """Manages conversation sessions for multiple users, including state."""
    def __init__(self):
        # Session stores history and the current state of the conversation.
        self._sessions = {}

    def get_session(self, session_id: str):
        """Retrieves the entire session object for a given ID."""
        return self._sessions.get(session_id)

    def update_state(self, session_id: str, new_state: str):
        """Updates the state of a conversation."""
        if session_id in self._sessions:
            self._sessions[session_id]['state'] = new_state

    def start_new_session(self, session_id: str, system_message: SystemMessage):
        """Creates a new conversation history and sets the initial state."""
        self._sessions[session_id] = {
            'history': [system_message],
            'state': 'AWAITING_INITIAL_QUERY' # Initial state
        }
        return self._sessions[session_id]