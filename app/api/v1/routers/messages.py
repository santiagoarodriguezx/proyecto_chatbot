"""
Rutas de mensajes
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import MessageResponse, SendMessageRequest
from app.services.database import insert_row
from app.services.message_service import message_processor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=MessageResponse)
async def process_message(payload: SendMessageRequest):
    """Procesar mensaje manualmente (sin Evolution)"""
    phone = payload.get_phone()
    text = payload.get_message()

    if not phone:
        raise HTTPException(status_code=400, detail="Missing phone number")
    if not text:
        raise HTTPException(status_code=400, detail="Missing message text")

    try:
        # Generar respuesta usando el agente
        ai_response = message_processor.agent.invoke(
            {"input": text}).get("output", "Error")

        # Guardar en DB
        if insert_row:
            try:
                insert_row("message_logs", {
                           "phone_number": phone, "message_text": text, "direction": "incoming", "status": "received"})
                insert_row("message_logs", {
                           "phone_number": phone, "message_text": ai_response, "direction": "outgoing", "status": "sent"})
            except Exception as db_error:
                logger.warning(f"Error guardando en DB: {db_error}")

        return MessageResponse(success=True, message="OK", data={"to": phone, "request_preview": text[:160], "response": ai_response})
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))
