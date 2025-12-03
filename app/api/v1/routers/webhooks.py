"""
Rutas de webhooks de Evolution API
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from app.schemas.models import EvolutionWebhook, MessageResponse
from app.services.webhook_service import process_message_upsert
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Estadísticas
stats = {
    "total_events": 0,
    "messages_processed": 0,
    "errors": 0,
    "start_time": datetime.now().isoformat()
}


@router.post("/chats-update")
async def chats_update(request: Request):
    """Evento: Chat actualizado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("🔄 Chat updated")
    return {"status": "success", "event": "chats-update", "timestamp": datetime.now().isoformat()}


@router.post("/chats-upsert")
async def chats_upsert(request: Request):
    """Evento: Chat creado/actualizado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("📝 Chat upserted")
    return {"status": "success", "event": "chats-upsert", "timestamp": datetime.now().isoformat()}


@router.post("/messages-set")
async def messages_set(request: Request):
    """Evento: Mensajes configurados"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("📨 Messages set")
    return {"status": "success", "event": "messages-set", "timestamp": datetime.now().isoformat()}


@router.post("/messages-update")
async def messages_update(request: Request):
    """Evento: Mensaje actualizado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("🔄 Message updated")
    return {"status": "success", "event": "messages-update", "timestamp": datetime.now().isoformat()}


@router.post("/messages-upsert", response_model=MessageResponse)
async def messages_upsert(webhook: EvolutionWebhook):
    """Evento: Mensaje nuevo - SE PROCESA CON IA"""
    try:
        stats["total_events"] += 1
        logger.info(f"✉️ Message upserted from instance: {webhook.instance}")

        if not webhook.data.get("key"):
            raise HTTPException(
                status_code=400, detail="Missing 'key' in data")
        if not webhook.data.get("message"):
            raise HTTPException(
                status_code=400, detail="Missing 'message' in data")

        result = process_message_upsert(webhook)

        return MessageResponse(
            success=True,
            message="Mensaje procesado correctamente",
            data={"event": "messages-upsert", "instance": webhook.instance,
                  "timestamp": datetime.now().isoformat(), "processing": result}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        stats["errors"] += 1
        raise HTTPException(
            status_code=500, detail=f"Error interno procesando mensaje: {str(e)}")


@router.post("/send-message")
async def send_message_event(request: Request):
    """Evento: Mensaje enviado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("📤 Message sent")
    return {"status": "success", "event": "send-message", "timestamp": datetime.now().isoformat()}


@router.get("/stats")
def get_stats():
    """Obtener estadísticas de webhooks"""
    return {"statistics": stats, "timestamp": datetime.now().isoformat()}
