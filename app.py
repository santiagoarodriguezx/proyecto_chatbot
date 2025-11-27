"""
API Profesional para Evolution WhatsApp Bot
Maneja todos los eventos de Evolution API con logging y validación
"""

from ai_service import ai_service
from src.api.models.models import EvolutionWebhook, MessageResponse, SendMessageRequest
from message_processor import message_processor
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any
import logging
import sys
import os
from send_message import process_message_upsert

# Agregar el directorio raíz al path para importar los modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Evolution WhatsApp AI Bot",
    description="API profesional para procesar eventos de Evolution API con IA",
    version="1.0.0"
)

# Estadísticas
stats = {
    "total_events": 0,
    "messages_processed": 0,
    "errors": 0,
    "start_time": datetime.now().isoformat()
}


@app.post("/chats-update")
async def chats_update(request: Request):
    """Evento: Chat actualizado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("🔄 Chat updated")
    return {
        "status": "success",
        "event": "chats-update",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chats-upsert")
async def chats_upsert(request: Request):
    """Evento: Chat creado/actualizado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("📝 Chat upserted")
    return {
        "status": "success",
        "event": "chats-upsert",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/messages-set")
async def messages_set(request: Request):
    """Evento: Mensajes configurados"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("📨 Messages set")
    return {
        "status": "success",
        "event": "messages-set",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/messages-update")
async def messages_update(request: Request):
    """Evento: Mensaje actualizado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("🔄 Message updated")
    return {
        "status": "success",
        "event": "messages-update",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/messages-upsert", response_model=MessageResponse)
async def messages_upsert(webhook: EvolutionWebhook):
    """
    Evento: Mensaje nuevo - SE PROCESA CON IA

    Recibe un webhook de Evolution API con la estructura:
    - event: Tipo de evento (messages.upsert)
    - instance: Nombre de la instancia
    - data: Datos del mensaje que incluyen:
        - key: Información de la clave (remoteJid, fromMe)
        - message: Contenido del mensaje (conversation o extendedTextMessage)

    Este endpoint VALIDA que reciba:
    - Un número de teléfono válido (remoteJid)
    - Un texto de mensaje (conversation o extendedTextMessage.text)
    """
    try:
        stats["total_events"] += 1
        logger.info(f"✉️ Message upserted from instance: {webhook.instance}")

        # Validar que tenga los campos mínimos requeridos
        if not webhook.data.get("key"):
            raise HTTPException(
                status_code=400,
                detail="Missing 'key' in data. Required: key.remoteJid"
            )

        if not webhook.data.get("message"):
            raise HTTPException(
                status_code=400,
                detail="Missing 'message' in data. Required: message.conversation or message.extendedTextMessage.text"
            )

        # Procesar el mensaje con IA
        result = process_message_upsert(webhook)

        return MessageResponse(
            success=True,
            message="Mensaje procesado correctamente",
            data={
                "event": "messages-upsert",
                "instance": webhook.instance,
                "timestamp": datetime.now().isoformat(),
                "processing": result
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        stats["errors"] += 1
        raise HTTPException(
            status_code=500,
            detail=f"Error interno procesando mensaje: {str(e)}"
        )


@app.post("/send-message")
async def send_message_event(request: Request):
    """Evento: Mensaje enviado"""
    data = await request.json()
    stats["total_events"] += 1
    logger.info("📤 Message sent")
    return {
        "status": "success",
        "event": "send-message",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/process-message", response_model=MessageResponse)
async def process_message_anywhere(payload: SendMessageRequest):
    """Recibe un mensaje desde cualquier cliente (Postman, otro servicio, etc.), lo procesa con la IA y devuelve la respuesta.

    Requiere al menos un número y un texto (en `numero`/`phone` y `texto`/`message`).
    """
    phone = payload.get_phone()
    text = payload.get_message()

    if not phone:
        raise HTTPException(
            status_code=400, detail="Missing phone number (numero or phone)")
    if not text:
        raise HTTPException(
            status_code=400, detail="Missing message text (texto or message)")

    try:
        # Prompt simple y consistente
        prompt = f"Eres un asistente útil y conciso. Usuario ({phone}): {text}\n\nAsistente:"
        ai_response = ai_service.generate_response(prompt)

        # Responder con el formato estándar
        return MessageResponse(
            success=True,
            message="OK",
            data={
                "to": phone,
                "request_preview": text[:160],
                "response": ai_response
            }
        )
    except Exception as e:
        logger.error(f"Error procesando /process-message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """Endpoint raíz - Información del bot"""
    return {
        "status": "online",
        "bot": "Evolution WhatsApp AI",
        "version": "1.0.0",
        "description": "Bot profesional con IA para WhatsApp vía Evolution API",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "docs": "/docs",
            "events": "Total de 26 endpoints POST para eventos de Evolution"
        }
    }


@app.get("/health")
def health_check():
    """Health check - Estado del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_since": stats["start_time"]
    }


@app.get("/stats")
def get_stats():
    """Obtener estadísticas del bot"""
    return {
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Servidor iniciando en http://0.0.0.0:8000")
    logger.info("📚 Documentación disponible en http://0.0.0.0:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
