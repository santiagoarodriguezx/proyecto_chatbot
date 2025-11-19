"""
Modelos Pydantic para la API FastAPI
Define las estructuras de datos para requests y responses
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class WhatsAppMessage(BaseModel):
    """Modelo para mensajes entrantes del webhook con soporte multimedia"""
    from_number: str = Field(..., description="Número que envía el mensaje")
    to_number: str = Field(..., description="Número que recibe el mensaje")
    message_text: Optional[str] = Field(None, description="Texto del mensaje")
    message_type: str = Field(
        default="text", description="Tipo de mensaje (text, image, audio)")
    timestamp: Optional[str] = Field(None, description="Timestamp del mensaje")
    message_id: Optional[str] = Field(None, description="ID único del mensaje")
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_number": "5511999999999",
                "to_number": "bot",
                "message_text": "Hola, quiero información",
                "message_type": "text",
                "message_id": "MSG123"
            }
        }


class SendMessageRequest(BaseModel):
    """Modelo para solicitudes de envío de mensaje"""
    numero: Optional[str] = Field(None, description="Número de destinatario")
    phone: Optional[str] = Field(
        None, description="Número de destinatario (alternativo)")
    texto: Optional[str] = Field(None, description="Texto a enviar")
    message: Optional[str] = Field(
        None, description="Texto a enviar (alternativo)")

    class Config:
        json_schema_extra = {
            "example": {
                "numero": "5511999999999",
                "texto": "Gracias por contactarnos"
            }
        }

    def get_phone(self) -> str:
        """Obtener número de teléfono de cualquier campo"""
        return self.numero or self.phone or ""

    def get_message(self) -> str:
        """Obtener mensaje de cualquier campo"""
        return self.texto or self.message or ""


class MessageResponse(BaseModel):
    """Modelo para respuestas de la API"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Mensaje procesado correctamente",
                "data": {
                    "message_id": "MSG123",
                    "timestamp": "2025-10-07T12:00:00"
                }
            }
        }


class EvolutionWebhook(BaseModel):
    """Modelo para webhooks de Evolution API"""
    event: str = Field(..., description="Tipo de evento")
    instance: str = Field(..., description="Nombre de la instancia")
    data: Dict[str, Any] = Field(..., description="Datos del webhook")

    class Config:
        json_schema_extra = {
            "example": {
                "event": "messages.upsert",
                "instance": "ia-whatsapp",
                "data": {
                    "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
                    "message": {"conversation": "Hola"}
                }
            }
        }
