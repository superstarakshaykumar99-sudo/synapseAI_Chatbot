import os
import streamlit as st
import uuid
from datetime import datetime
from groq import Groq

# ─── Config ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

st.set_page_config(
    page_title="SynapseAI Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    .stApp {
        background-color: #0b0914 !important;
        background-image: none !important;
        color: #e5e5e5 !important;
    }
    [data-testid="stAppViewContainer"] { background-color: #0b0914 !important; }
    header[data-testid="stHeader"] {
        background-color: #0b0914 !important;
        border-bottom: 1px solid #1a1727;
    }
    [data-testid="stSidebar"] {
        background-color: #110e1b !important;
        border-right: 1px solid #1a1727 !important;
    }
    h1, h2, h3, p, span, div, li {
        color: #e2e2e2 !important;
        font-weight: 500;
    }
    .stChatMessage [data-testid="chatAvatarIcon-user"],
    .stChatMessage [data-testid="chatAvatarIcon-assistant"],
    div[data-testid="stChatMessage"] > div:first-child { display: none !important; }
    .stChatMessage {
        background-color: #171523 !important;
        border: 1px solid #28243d !important;
        border-radius: 12px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
        width: 100% !important;
        max-width: 900px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        box-shadow: none !important;
    }
    .stChatMessage:hover { border-color: #3b3559 !important; }
    .stChatMessage p {
        font-size: 15px !important;
        color: #d1d1d1 !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
    }
    .stChatInputContainer {
        padding: 20px;
        background-color: #0b0914 !important;
        border-top: none !important;
        max-width: 900px;
        margin: 0 auto;
    }
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #211e33 !important;
        border: 1px solid #332d4e !important;
        box-shadow: none !important;
        padding: 4px 10px !important;
    }
    [data-testid="stChatInput"]:focus-within { border-color: #5b4ead !important; }
    [data-testid="stChatInput"] button {
        background-color: #553b9a !important;
        border-radius: 50% !important;
        color: white !important;
    }
    .stButton > button {
        background-color: #211e33 !important;
        border: 1px solid #332d4e !important;
        border-radius: 20px !important;
        color: #e2e2e2 !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        box-shadow: none !important;
        transition: background-color 0.2s !important;
        background-image: none !important;
    }
    .stButton > button:hover {
        background-color: #312d4a !important;
        border-color: #332d4e !important;
    }
    [data-testid="stSidebar"] button:first-of-type {
        background: linear-gradient(90deg, #4b2c91, #30176d) !important;
        border: 1px solid #5b3fb0 !important;
    }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0b0914; }
    ::-webkit-scrollbar-thumb { background: #2a2640; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #3b3559; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []


# ─── Groq Chat Function ───────────────────────────────────────────────────────
def build_system_prompt() -> str:
    now = datetime.now()
    return (
        f"You are SynapseAI, a highly intelligent, precise, and helpful AI assistant.\n"
        f"Today's date is {now.strftime('%A, %d %B %Y')} and the current time is "
        f"{now.strftime('%I:%M %p')} (IST). Always use this as the authoritative current date/time.\n"
        f"Be concise, accurate, and helpful."
    )


def stream_groq_response(messages: list):
    if not client:
        yield "⚠️ GROQ_API_KEY is not configured. Please add it in Streamlit Cloud secrets."
        return
    try:
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=2048,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"An error occurred: {str(e)}"


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 SynapseAI")
    st.markdown("**PRO** `v1.0`")
    st.markdown(f"**Session:** `{st.session_state.session_id}`")
    st.divider()

    st.markdown("**Model:** `llama-3.3-70b`")
    st.markdown("**Provider:** `Groq ⚡`")
    st.divider()

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        "<small style='color:#555'>Built with ❤️ using Groq + Streamlit</small>",
        unsafe_allow_html=True
    )


# ─── Main Chat Window ─────────────────────────────────────────────────────────
st.header("Chat with your Data")

# Display existing messages
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "assistant" else "user"
    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🧠"):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to UI and state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Build message history for Groq
    groq_messages = [{"role": "system", "content": build_system_prompt()}]
    for m in st.session_state.messages:
        groq_messages.append({"role": m["role"], "content": m["content"]})

    # Stream the response
    with st.chat_message("assistant", avatar="🧠"):
        response_placeholder = st.empty()
        full_response = ""

        for chunk in stream_groq_response(groq_messages):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    # Save to session state
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
