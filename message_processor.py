"""
Message Processor - Procesador simple de mensajes
Recibe mensajes de Evolution y los envía a la IA con un prompt básico
"""

import requests
import os
from dotenv import load_dotenv
from ai_service import ai_service

load_dotenv()


class MessageProcessor:
    """Procesador simple de mensajes para chatbot"""

    def __init__(self):
        """Inicializar el procesador de mensajes"""
        self.ai = ai_service
        self.evolution_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance = os.getenv("EVOLUTION_INSTANCE", "ia-whatsapp")

    def process_and_reply(self, message_text: str, from_number: str):
        """
        Procesar mensaje y enviar respuesta a Evolution

        Args:
            message_text: Texto del mensaje recibido
            from_number: Número del remitente
        """
        try:
            print(f"📨 Mensaje de {from_number}: {message_text}")

            # Generar respuesta con IA
            prompt = f"""Eres un asistente virtual amigable y útil.

Usuario: {message_text}

Asistente:"""

            response = self.ai.generate_response(prompt)
            print(f"🤖 Respuesta: {response[:100]}...")

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
