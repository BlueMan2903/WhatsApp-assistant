import sqlite3
import json
import os
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, BaseMessage, 
    messages_from_dict, messages_to_dict
)

class ConversationManager:
    def __init__(self, db_path="data/sessions.db"):
        self.db_path = db_path
        # Ensure the data directory exists for the SQLite file
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    history TEXT,
                    state TEXT,
                    user_name TEXT,
                    user_phone TEXT,
                    price_menu_sent INTEGER DEFAULT 0
                )
            ''')

    def get_session(self, session_id: str):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT history, state FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if row:
                return {
                    'history': messages_from_dict(json.loads(row[0])),
                    'state': row[1]
                }
        return None

    def save_history(self, session_id: str, history: list[BaseMessage], state: str):
        history_json = json.dumps(messages_to_dict(history))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE sessions SET history = ?, state = ? WHERE session_id = ?",
                (history_json, state, session_id)
            )

    def start_new_session(self, session_id: str, system_message: SystemMessage):
        initial_greeting = AIMessage(content="שלום, הגעת לקליניקה של ניקול. אני העוזרת שלה, איך אוכל לעזור?")
        history_json = json.dumps(messages_to_dict([system_message, initial_greeting]))
        state = 'AWAITING_INITIAL_QUERY'
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, history, state) VALUES (?, ?, ?)",
                (session_id, history_json, state)
            )
        return {'history':[system_message, initial_greeting], 'state': state}

    def update_state(self, session_id: str, new_state: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE sessions SET state = ? WHERE session_id = ?", (new_state, session_id))

    def update_data(self, session_id: str, key: str, value: str):
        allowed_keys = ['user_name', 'user_phone', 'price_menu_sent']
        if key in allowed_keys:
            if key == 'price_menu_sent': value = 1 if value else 0
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"UPDATE sessions SET {key} = ? WHERE session_id = ?", (value, session_id))

    def get_data(self, session_id: str, key: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
            if row and key in row.keys():
                return row[key]
        return None

    def reset_session(self, session_id: str, system_message: SystemMessage):
        self.start_new_session(session_id, system_message)

    def get_formatted_history(self, session_id: str) -> str:
        session = self.get_session(session_id)
        if not session: return "No history."
        lines = []
        for m in session['history']:
            if isinstance(m, HumanMessage): lines.append(f"User: {m.content}")
            elif isinstance(m, AIMessage): lines.append(f"Lola: {m.content}")
        return "\n".join(lines)