import sqlite3
import datetime
from app.config import DB_PATH
from utils.logger import logger

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Simple indexing for faster session lookups
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)
            ''')
            conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

def save_message(session_id: str, role: str, content: str):
    try:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
                (session_id, role, content)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to save message: {e}")

def get_history(session_id: str, limit: int = 50):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                'SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?',
                (session_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return []

def clear_history(session_id: str):
    try:
        with get_db_connection() as conn:
            conn.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        return False
        
# Initialize on import
init_db()
