import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SynapseAI Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for DeepAI Clone UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Flat Dark Purple/Navy Background matching DeepAI */
    .stApp {
        background-color: #0b0914 !important;
        background-image: none !important;
        animation: none !important;
        color: #e5e5e5 !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #0b0914 !important;
    }

    /* Top Nav (Hidden natively, but we ensure cleanliness) */
    header[data-testid="stHeader"] {
        background-color: #0b0914 !important;
        border-bottom: 1px solid #1a1727;
    }

    /* Sidebar - Flat slightly lighter purple */
    [data-testid="stSidebar"] {
        background-color: #110e1b !important;
        border-right: 1px solid #1a1727 !important;
    }
    
    /* Headers & Text */
    h1, h2, h3, p, span, div, li {
        color: #e2e2e2 !important;
        letter-spacing: normal !important;
        text-shadow: none !important;
        font-weight: 500;
    }
    
    /* Completely hide the Streamlit avatars to match DeepAI */
    .stChatMessage [data-testid="chatAvatarIcon-user"],
    .stChatMessage [data-testid="chatAvatarIcon-assistant"],
    div[data-testid="stChatMessage"] > div:first-child {
        display: none !important;
    }

    /* Message Bubbles - Flat, wide, rounded rectangles exactly like DeepAI */
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
        animation: none !important;
        transform: none !important;
    }
    
    .stChatMessage:hover {
        transform: none !important;
        box-shadow: none !important;
        border-color: #3b3559 !important;
    }
    
    /* Both user and AI messages share the exact same style in DeepAI */
    .stChatMessage[data-testid="chat-message-user"],
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-image: none !important;
        border-left: 1px solid #28243d !important;
        border-right: 1px solid #28243d !important;
    }
    
    /* Text inside messages */
    .stChatMessage p {
        font-size: 15px !important;
        color: #d1d1d1 !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
    }

    /* The Chat Input Dock */
    .stChatInputContainer {
        padding: 20px;
        background-color: #0b0914 !important;
        border-top: none !important;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Input field */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #211e33 !important;
        border: 1px solid #332d4e !important;
        box-shadow: none !important;
        padding: 4px 10px !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: #5b4ead !important;
        box-shadow: none !important;
    }

    /* Send button icon inside input area */
    [data-testid="stChatInput"] button {
        background-color: #553b9a !important;
        border-radius: 50% !important;
        color: white !important;
    }

    /* Sidebar Buttons - Exact Match */
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
    
    .stButton > button::before {
        display: none !important;
    }
    
    .stButton > button:hover {
        background-color: #312d4a !important;
        border-color: #332d4e !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Simulating 'Upgrade to DeepAI Pro' purple button */
    [data-testid="stSidebar"] button:first-of-type {
        background: linear-gradient(90deg, #4b2c91, #30176d) !important;
        border: 1px solid #5b3fb0 !important;
    }
    [data-testid="stSidebar"] button:first-of-type:hover {
        background: linear-gradient(90deg, #5b3fb0, #3e1b8c) !important;
    }

    /* File Uploader styling */
    [data-testid="stFileUploader"] section {
        background-color: #171523 !important;
        border: 1px dashed #332d4e !important;
        border-radius: 8px !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0b0914; }
    ::-webkit-scrollbar-thumb {
        background: #2a2640;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #3b3559; }

</style>
""", unsafe_allow_html=True)

# Generate or get Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Try fetching previous history from API
    try:
        res = requests.get(f"{API_URL}/history/{st.session_state.session_id}")
        if res.status_code == 200:
            history = res.json().get("history", [])
            for msg in history:
                st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
    except:
        pass


# ─── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 SynapseAI")
    st.markdown("**PRO** `v1.0`")
    st.markdown(f"**Session:** `{st.session_state.session_id}`")
    
    st.divider()
    
    st.subheader("📄 Knowledge Base")
    st.caption("Upload a PDF to chat with it")
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        if st.button("⚡ Index PDF", use_container_width=True, key="process_pdf"):
            with st.spinner("Processing..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    res = requests.post(f"{API_URL}/upload-pdf", files=files)
                    if res.status_code == 200:
                        st.success("PDF indexed successfully!")
                    else:
                        st.error(f"Error: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Backend server is not running.")
                    
    st.divider()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        try:
            requests.delete(f"{API_URL}/history/{st.session_state.session_id}")
            st.session_state.messages = []
            st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("Backend server is not running.")

# ─── Main Chat Window ────────────────────────────────────────────────────
st.header("Chat with your Data")

# Display chat messages from history
for message in st.session_state.messages:
    # Handle role naming difference between our backend (assistant) and Streamlit (assistant)
    role = "assistant" if message["role"] == "assistant" or message["role"] == "model" else "user"
    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🧠"):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Display assistant response with a placeholder
    with st.chat_message("assistant", avatar="🧠"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream the response from the FastAPI backend
            with requests.post(
                f"{API_URL}/chat", 
                json={"session_id": st.session_state.session_id, "query": prompt},
                stream=True
            ) as response:
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            full_response += chunk
                            response_placeholder.markdown(full_response + "▌")
                    # Final update without the cursor
                    response_placeholder.markdown(full_response)
                else:
                    st.error(f"Error: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend API. Please ensure it is running (`sh run.sh`).")
        
        # Add assistant response to history
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
