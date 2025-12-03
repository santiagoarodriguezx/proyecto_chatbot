"""
Rutas de conversaciones
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import MessageResponse
from app.services.database import _client
from app.services.message_service import message_processor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=MessageResponse)
def list_conversations(limit: int = 20, active_only: bool = False):
    """Listar conversaciones"""
    try:
        query = _client.table("conversations").select("*")
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
    try:
        messages = _client.table("message_logs").select(
            "*").eq("phone_number", phone_number).order("created_at", desc=True).limit(limit).execute()
        conversation = _client.table("conversations").select(
            "*").eq("phone_number", phone_number).single().execute()
        return MessageResponse(success=True, message="Historial recuperado", data={"phone_number": phone_number, "message_count": len(messages.data), "messages": messages.data, "conversation_info": conversation.data if conversation.data else None})
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{phone_number}")
def delete_conversation(phone_number: str):
    """Eliminar conversación"""
    try:
        _client.table("message_logs").delete().eq(
            "phone_number", phone_number).execute()
        _client.table("conversations").delete().eq(
            "phone_number", phone_number).execute()
        return {"success": True, "message": f"Conversación {phone_number} eliminada"}
    except Exception as e:
        logger.error(f"Error eliminando conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/reset/{phone_number}")
def reset_memory(phone_number: str):
    """Resetear memoria de conversación"""
    try:
        message_processor.memory.clear()
        _client.table("conversations").update({"context": {}, "current_state": "reset"}).eq(
            "phone_number", phone_number).execute()
        return {"success": True, "message": f"Memoria reseteada para {phone_number}"}
    except Exception as e:
        logger.error(f"Error reseteando memoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))
