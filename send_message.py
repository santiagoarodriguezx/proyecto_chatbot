from message_processor import message_processor
from src.api.models.models import EvolutionWebhook
from typing import Dict, Any
import logging


# Configurar logging local
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_message_upsert(webhook: EvolutionWebhook) -> Dict[str, Any]:
    """Procesar mensaje nuevo y responder con IA"""
    try:
        # Extraer datos del webhook validado
        message_data = webhook.data
        key = message_data.get("key", {})
        message = message_data.get("message", {})

        # Verificar que no sea mensaje del bot

        # Obtener número del remitente
        remote_jid = key.get("remoteJid", "")
        if not remote_jid:
            return {"action": "error", "reason": "missing_remote_jid"}

        from_number = remote_jid.replace("@s.whatsapp.net", "")

        # Obtener texto del mensaje
        message_text = (
            message.get("conversation") or
            message.get("extendedTextMessage", {}).get("text") or
            ""
        )

        if not message_text:
            return {"action": "skipped", "reason": "no_message_text"}

        if not from_number:
            return {"action": "skipped", "reason": "no_phone_number"}

        logger.info(
            f"💬 Procesando mensaje de {from_number}: {message_text[:50]}...")
        message_processor.process_and_reply(message_text, from_number)

        return {
            "action": "processed",
            "from": from_number,
            "message_preview": message_text[:100]
        }

    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {str(e)}")
        raise
