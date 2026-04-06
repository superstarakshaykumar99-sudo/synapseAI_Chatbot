import os
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse, JSONResponse
from pydantic import BaseModel

from app.chatbot import generate_response
from app.pdf_handler import process_pdf
from app.database import get_history, clear_history
from app.whatsapp import handle_whatsapp_message
from app.config import DOCS_DIR
from utils.logger import logger

app = FastAPI(title="SynapseAI Chatbot API")

class ChatRequest(BaseModel):
    session_id: str
    query: str

@app.get("/")
def read_root():
    return {"message": "SynapseAI Backend is running."}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Standard chat endpoint supporting streaming responses.
    """
    # Create the generator for streaming
    generator = generate_response(request.session_id, request.query)
    
    # Return as Server-Sent Events (SSE) or simple text stream
    return StreamingResponse(generator, media_type="text/plain")

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Uploads a PDF and processes it for RAG.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(DOCS_DIR, file.filename)
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    logger.info(f"File saved to {file_path}")
    
    # Process for Vector DB
    success, message = process_pdf(file_path)
    
    if success:
        return JSONResponse(content={"status": "success", "message": message})
    else:
        # Clean up failed file
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=message)

@app.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    history = get_history(session_id)
    return {"session_id": session_id, "history": history}

@app.delete("/history/{session_id}")
async def delete_chat_history(session_id: str):
    success = clear_history(session_id)
    if success:
        return {"status": "success", "message": f"History cleared for session {session_id}"}
    raise HTTPException(status_code=500, detail="Failed to clear history")

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Twilio Webhook Endpoint for WhatsApp.
    Receives FormURL encoded data.
    """
    form_data = await request.form()
    
    sender = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    
    if not sender or not message_body:
        raise HTTPException(status_code=400, detail="Invalid Request")
        
    twiml_response = handle_whatsapp_message(sender, message_body)
    
    return PlainTextResponse(content=twiml_response, media_type="application/xml")
