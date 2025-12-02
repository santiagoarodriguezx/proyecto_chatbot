from message_processor import message_processor
from src.api.models.models import EvolutionWebhook
from typing import Dict, Any
import logging
from datetime import datetime

# Import opcional del cliente Supabase. Si la dependencia o el archivo no existen,
# dejamos `insert_row` como None para no romper la aplicación.
try:
    from supabase_client import insert_row
except Exception:
    insert_row = None


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

        # Guardar en la tabla `message_logs` si el cliente Supabase está disponible
        if insert_row:
            try:
                payload = {
                    "phone_number": from_number,
                    "message_text": message_text,
                    "direction": "incoming",
                    "status": "received"
                }
                insert_row("message_logs", payload)
            except Exception as e:
                logger.warning(f"No se pudo guardar mensaje en Supabase: {e}")

        message_processor.process_and_reply(message_text, from_number)

        return {
            "action": "processed",
            "from": from_number,
            "message_preview": message_text[:100]
        }

    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {str(e)}")
        raise
