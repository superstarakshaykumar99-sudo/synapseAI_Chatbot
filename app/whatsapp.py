from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from utils.logger import logger
from app.chatbot import generate_response_sync

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def handle_whatsapp_message(sender: str, message_body: str) -> str:
    """
    Processes incoming WhatsApp message, gets AI response, and formats TwiML response.
    We use the sender's phone number as the session ID to maintain memory.
    """
    logger.info(f"Received WhatsApp message from {sender}: {message_body}")
    
    # Use the phone number as the session ID
    session_id = f"wa_{sender.replace('whatsapp:', '')}"
    
    # Get AI response synchronously (Twilio Webhooks don't support streaming)
    ai_response = generate_response_sync(session_id, message_body)
    
    # Send a long message directly via API if it exceeds TwiML limits,
    # but for simplicity, we return TwiML here.
    twiml_response = MessagingResponse()
    msg = twiml_response.message()
    msg.body(ai_response)
    
    return str(twiml_response)
