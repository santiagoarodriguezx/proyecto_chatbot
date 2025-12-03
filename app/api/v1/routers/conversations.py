"""
Rutas de conversaciones
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import MessageResponse
from app.services.supabase_service import supabase_service
from app.services.message_service import message_processor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=MessageResponse)
def list_conversations(limit: int = 20, active_only: bool = False):
    """Listar conversaciones"""
    if not supabase_service.is_available():
        raise HTTPException(status_code=503, detail="Supabase no disponible")

    try:
        client = supabase_service.client
        query = client.table("conversations").select("*")
        if active_only:
            query = query.eq("current_state", "active")
        result = query.order(
            "last_message_at", desc=True).limit(limit).execute()
        return MessageResponse(success=True, message="Conversaciones recuperadas", data={"count": len(result.data), "conversations": result.data})
    except Exception as e:
        logger.error(f"Error listando conversaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{phone_number}", response_model=MessageResponse)
def get_conversation_history(phone_number: str, limit: int = 50):
    """Obtener historial de conversación"""
    if not supabase_service.is_available():
        raise HTTPException(status_code=503, detail="Supabase no disponible")

    try:
        messages = supabase_service.get_conversation_history(
            phone_number, limit)
        client = supabase_service.client
        conversation = client.table("conversations").select(
            "*").eq("phone_number", phone_number).single().execute()
        return MessageResponse(success=True, message="Historial recuperado", data={"phone_number": phone_number, "message_count": len(messages), "messages": messages, "conversation_info": conversation.data if conversation.data else None})
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{phone_number}")
def delete_conversation(phone_number: str):
    """Eliminar conversación"""
    if not supabase_service.is_available():
        raise HTTPException(status_code=503, detail="Supabase no disponible")

    try:
        client = supabase_service.client
        client.table("message_logs").delete().eq(
            "phone_number", phone_number).execute()
        client.table("conversations").delete().eq(
            "phone_number", phone_number).execute()
        return {"success": True, "message": f"Conversación {phone_number} eliminada"}
    except Exception as e:
        logger.error(f"Error eliminando conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e))
