from app.database import get_history, save_message
from app.config import MEMORY_WINDOW
from utils.logger import logger

class ConversationMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        
    def add_user_message(self, content: str):
        logger.debug(f"Adding user message to session {self.session_id}")
        save_message(self.session_id, "user", content)
        
    def add_ai_message(self, content: str):
        logger.debug(f"Adding AI message to session {self.session_id}")
        save_message(self.session_id, "assistant", content)
        
    def get_context(self) -> list[dict]:
        """
        Retrieves the last N messages to provide as context to the LLM.
        Limits to MEMORY_WINDOW to prevent token overflow.
        """
        full_history = get_history(self.session_id, limit=MEMORY_WINDOW)
        return full_history

def get_memory_for_session(session_id: str) -> ConversationMemory:
    return ConversationMemory(session_id)
