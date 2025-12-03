"""
Rutas de mensajes
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import MessageResponse, SendMessageRequest
from app.services.supabase_service import supabase_service
from app.services.message_service import message_processor
from app.core.ia_service import ia_service
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
        # Generar respuesta usando el servicio de IA
        ai_response = ia_service.generate_response(text)

        # Guardar en DB usando supabase_service
        try:
            supabase_service.get_or_create_conversation(phone)
            supabase_service.save_message_log(
                phone_number=phone,
                message_text=text,
                direction="incoming",
                status="received"
            )
            supabase_service.save_message_log(
                phone_number=phone,
                message_text=ai_response,
                direction="outgoing",
                status="sent"
            )
        except Exception as db_error:
            logger.warning(f"Error guardando en DB: {db_error}")

        return MessageResponse(success=True, message="OK", data={"to": phone, "request_preview": text[:160], "response": ai_response})
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))
