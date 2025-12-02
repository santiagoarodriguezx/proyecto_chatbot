"""
Message Processor - Procesador simple de mensajes
Recibe mensajes de Evolution y los envía a la IA con un prompt básico
"""

import requests
import os
from dotenv import load_dotenv
from ai_service import ai_service

try:
    from supabase_client import fetch_prompt_by_name, insert_row
except Exception:
    fetch_prompt_by_name = None
    insert_row = None

load_dotenv()


class MessageProcessor:
    """Procesador simple de mensajes para chatbot"""

    def __init__(self):
        """Inicializar el procesador de mensajes"""
        self.ai = ai_service
        self.evolution_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance = os.getenv("EVOLUTION_INSTANCE", "ia-whatsapp")
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Cargar el prompt system_welcome desde Supabase"""
        if not fetch_prompt_by_name:
            print("⚠️ Supabase no disponible, usando prompt por defecto")
            return "Eres un asistente virtual amigable y útil."

        try:
            prompt_data = fetch_prompt_by_name("system_welcome")
            if prompt_data and "content" in prompt_data:
                print(f"✅ Prompt 'system_welcome' cargado desde Supabase")
                return prompt_data["content"]
            else:
                print(
                    "⚠️ Prompt 'system_welcome' no encontrado en Supabase, usando prompt por defecto")
                return "Eres un asistente virtual amigable y útil."
        except Exception as e:
            print(f"❌ Error cargando prompt desde Supabase: {str(e)}")
            return "Eres un asistente virtual amigable y útil."

    def process_and_reply(self, message_text: str, from_number: str):
        """
        Procesar mensaje y enviar respuesta a Evolution

        Args:
            message_text: Texto del mensaje recibido
            from_number: Número del remitente
        """
        try:
            print(f"📨 Mensaje de {from_number}: {message_text}")

            # Generar respuesta con IA usando el prompt de Supabase
            prompt = f"""{self.system_prompt}

Usuario: {message_text}

Asistente:"""

            response = self.ai.generate_response(prompt)
            print(f"🤖 Respuesta: {response[:100]}...")

            # Guardar respuesta en message_logs
            if insert_row:
                try:
                    insert_row("message_logs", {
                        "phone_number": from_number,
                        "message_text": response,
                        "direction": "outgoing",
                        "status": "sent"
                    })
                except Exception as e:
                    print(f"⚠️ No se pudo guardar respuesta en Supabase: {e}")

            # Enviar respuesta a Evolution
            self.send_to_evolution(from_number, response)

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.send_to_evolution(
                from_number, "Lo siento, hubo un error. Intenta de nuevo.")

    def send_to_evolution(self, number: str, text: str):
        """Enviar mensaje a Evolution API"""
        try:
            url = f"{self.evolution_url}/message/sendText/{self.instance}"
            headers = {
                "Content-Type": "application/json",
                "apikey": self.api_key
            }
            data = {
                "number": number,
                "text": text
            }

            response = requests.post(
                url, json=data, headers=headers, timeout=10)

            if response.status_code == 201:
                print(f"✅ Mensaje enviado a {number}")
            else:
                print(f"⚠️ Error enviando: {response.status_code}")

        except Exception as e:
            print(f"❌ Error enviando a Evolution: {str(e)}")


# Instancia global del procesador de mensajes
message_processor = MessageProcessor()
