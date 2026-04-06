# 🧠 SynapseAI Chatbot

A production-ready AI chatbot platform built with FastAPI, Streamlit, and RAG capabilities (Retrieval-Augmented Generation).

## Features

- **Multi-Model Support**: Easily switch between OpenAI (GPT-4o) and Google Gemini via `.env`.
- **RAG via FAISS**: Upload PDFs to the Streamlit UI, chunk them, embed them using `sentence-transformers`, and use them as context in chat.
- **Persistent Memory**: Chat history is stored in an SQLite `chats.db`. The system handles conversation rolling memory to avoid token limits.
- **Glassmorphic UI**: Polished Streamlit frontend using a dark, modern glass UI.
- **WhatsApp Integration**: Hooks into Twilio so you can chat via WhatsApp.
- **Streaming Responses**: Token-by-token rendering in the UI for a fast, ChatGPT-like experience.

## Setup Instructions

### 1. Requirements

Ensure you have Python 3.10+ installed.

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Open `.env` (it was instantiated from `.env.example`) and fill in your keys:

- `OPENAI_API_KEY=sk-...` (If using OpenAI)
- `GEMINI_API_KEY=AIza...` (If using Gemini)
- `AI_PROVIDER=openai` (Set to "openai" or "gemini")

*(Self-host or external providers optional)*

### 3. Running the App

The main runner script will start **both** FastAPI and Streamlit concurrently:

```bash
./run.sh
```

Or run them individually:
```bash
# Terminal 1 - Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
python -m streamlit run frontend/app.py
```

### WhatsApp Integration (Twilio)

1. Put your `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`.
2. Expose your local port 8000 to the web (e.g., using ngrok: `ngrok http 8000`).
3. Set your Twilio WhatsApp Sandbox webhook to: `https://<your-ngrok-url>.ngrok.app/whatsapp/webhook`
