# assistant/session.py
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

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
    
    # FOR TESTING PURPOSES ONLY
    def reset_session(self, session_id: str, system_message: SystemMessage):
        """Resets the conversation history for a given session ID."""
        if session_id in self._sessions:
            self._sessions[session_id]['history'] = [system_message]
            self._sessions[session_id]['state'] = 'AWAITING_INITIAL_QUERY'
            return True
        return False
    
    def get_formatted_history(self, session_id: str) -> str:
            """Formats the chat history into a simple, readable string."""
            session = self.get_session(session_id)
            if not session:
                return "No session history found."
            
            history: list[BaseMessage] = session.get('history', [])
            formatted_lines = []

            for msg in history:
                if isinstance(msg, SystemMessage):
                    # We don't need to send the full system prompt to Nikol
                    continue 
                elif isinstance(msg, HumanMessage):
                    prefix = "User:"
                    if isinstance(msg.content, list): # Handle multipart messages (text + image)
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