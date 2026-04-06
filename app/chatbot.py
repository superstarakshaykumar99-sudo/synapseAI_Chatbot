from openai import OpenAI
import google.generativeai as genai
from typing import Iterator
from datetime import datetime

from app.config import (
    OPENAI_API_KEY, 
    GEMINI_API_KEY, 
    AI_PROVIDER, 
    OPENAI_MODEL, 
    GEMINI_MODEL
)
from app.memory import get_memory_for_session
from app.pdf_handler import get_context_for_query
from utils.logger import logger

# Initialize clients
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(GEMINI_MODEL)


def _build_system_prompt(query: str, use_rag: bool = True) -> str:
    now = datetime.now()
    current_date = now.strftime("%A, %d %B %Y")
    current_time = now.strftime("%I:%M %p")
    
    base_prompt = (
        f"You are SynapseAI, a highly intelligent, precise, and helpful AI assistant.\n"
        f"Today's date is {current_date} and the current time is {current_time} (IST). "
        f"Always use this as the authoritative current date/time when asked.\n"
    )
    
    if use_rag:
        context = get_context_for_query(query)
        if context:
            base_prompt += f"\nUse the following provided context to answer the user's query if relevant.\n\nCONTEXT:\n{context}\n\n"
            
    base_prompt += "If the context doesn't contain the answer, rely on your general knowledge but mention that it's not in the provided documents."
    return base_prompt


def generate_response_openai(session_id: str, query: str) -> Iterator[str]:
    if not openai_client:
        yield "Error: OpenAI API key is not configured."
        return

    memory = get_memory_for_session(session_id)
    history = memory.get_context()
    
    system_prompt = _build_system_prompt(query)
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend([{"role": m["role"], "content": m["content"]} for m in history])
    messages.append({"role": "user", "content": query})

    logger.info(f"Sending query to OpenAI ({OPENAI_MODEL})...")
    try:
        stream = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            stream=True,
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
                
        # Save complete message to memory after stream finishes
        memory.add_user_message(query)
        memory.add_ai_message(full_response)
        
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        yield f"An error occurred: {str(e)}"


def generate_response_gemini(session_id: str, query: str) -> Iterator[str]:
    if not GEMINI_API_KEY:
        yield "Error: Gemini API key is not configured."
        return

    memory = get_memory_for_session(session_id)
    history = memory.get_context()
    
    system_prompt = _build_system_prompt(query)
    
    # Gemini uses slightly different history format
    formatted_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        formatted_history.append({"role": role, "parts": [msg["content"]]})
        
    # Inject system prompt into the first message or prepend it
    full_prompt = f"SYSTEM INSTRUCTIONS: {system_prompt}\\n\\nUSER QUERY: {query}"

    logger.info(f"Sending query to Gemini ({GEMINI_MODEL})...")
    try:
        chat = gemini_model.start_chat(history=formatted_history)
        response = chat.send_message(full_prompt, stream=True)
        
        full_response = ""
        for chunk in response:
            content = chunk.text
            full_response += content
            yield content
            
        memory.add_user_message(query)
        memory.add_ai_message(full_response)
        
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        yield f"An error occurred: {str(e)}"


def generate_response(session_id: str, query: str) -> Iterator[str]:
    """Router function to split between AI providers based on config."""
    if AI_PROVIDER == "openai":
        yield from generate_response_openai(session_id, query)
    elif AI_PROVIDER == "gemini":
        yield from generate_response_gemini(session_id, query)
    else:
        yield f"Error: Unknown AI provider '{AI_PROVIDER}'"

# Non-streaming version for WhatsApp / simple REST clients
def generate_response_sync(session_id: str, query: str) -> str:
    stream = generate_response(session_id, query)
    return "".join(list(stream))
