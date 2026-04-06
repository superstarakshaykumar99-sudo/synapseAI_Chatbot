import os
from dotenv import load_dotenv

load_dotenv()

# AI Providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# App Settings
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Memory
MEMORY_WINDOW = int(os.getenv("MEMORY_WINDOW", 10))

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, os.getenv("DB_PATH", "data/chats.db"))
DOCS_DIR = os.path.join(BASE_DIR, os.getenv("DOCS_DIR", "data/docs"))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, os.getenv("FAISS_INDEX_PATH", "embeddings/faiss_index"))

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Ensure directories exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
