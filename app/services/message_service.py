"""
Message Processor con LangChain, Memoria y Busqueda en Google
Procesador que usa ConversationChain con herramientas de busqueda
"""

import os
import time
from dotenv import load_dotenv
from typing import Optional

from app.core.ia_service import ia_service
from app.services.supabase_service import supabase_service
from app.services.evolution_service import evolution_service

load_dotenv()


class MessageProcessor:
    """Procesador de mensajes con LangChain, memoria y busqueda en Google"""

    def __init__(self):
        """Inicializar procesador con servicios"""
        # Usar servicios modularizados
        self.ia_service = ia_service
        self.supabase_service = supabase_service
        self.evolution_service = evolution_service

    def process_and_reply(self, message_text: str, from_number: str) -> None:
        """
        Procesar mensaje y enviar respuesta

        Args:
            message_text: Texto del mensaje
            from_number: Numero del remitente
        """
        start_time = time.time()
        incoming_message_log = None

        try:
            print(f"📨 Mensaje de {from_number}: {message_text}")

            # 1. Gestionar conversacion
            conversation = self.supabase_service.get_or_create_conversation(
                from_number)

            # 2. Guardar mensaje entrante
            incoming_message_log = self.supabase_service.save_message_log(
                phone_number=from_number,
                message_text=message_text,
                direction="incoming",
                status="received"
            )

            # 3. Generar respuesta con servicio de IA
            response = self.ia_service.generate_response(message_text)

            # Calcular tiempo de respuesta
            response_time_ms = int((time.time() - start_time) * 1000)

            print(f"🤖 Respuesta ({response_time_ms}ms): {response[:100]}...")
            # 4. enviar mensahje por evolution api
            result = self.evolution_service.send_text_message(
                from_number, response)

            # 5. Guardar mensaje saliente
            outgoing_message_log = self.supabase_service.save_message_log(
                phone_number=from_number,
                message_text=response,
                direction="outgoing",
                status="pending"
            )

            # 6. Guardar respuesta de IA con metricas
            self.supabase_service.save_ai_response(
                message_log_id=incoming_message_log["id"] if incoming_message_log else None,
                response_text=response,
                prompt_used=self.ia_service.system_prompt,
                model_used="gemini-flash-lite-latest",
                response_time_ms=response_time_ms
            )

            # 7. Actualizar estado del mensaje saliente
            if result.get("success"):
                if outgoing_message_log:
                    # Podriamos actualizar el status a "sent" aqui
                    pass
            else:
                print(f"⚠️ Error enviando mensaje: {result.get('error')}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            error_msg = "Lo siento, hubo un error procesando tu mensaje."

            # Guardar error en AI response
            if incoming_message_log:
                self.supabase_service.save_ai_response(
                    message_log_id=incoming_message_log["id"],
                    response_text=error_msg,
                    error_message=str(e),
                    response_time_ms=int((time.time() - start_time) * 1000)
                )

    def get_conversation_history(self, phone_number: str, limit: int = 10):
        """
        Obtener historial de conversacion

        Args:
            phone_number: Numero de telefono
            limit: Cantidad de mensajes

        Returns:
            Lista de mensajes
        """
        return self.supabase_service.get_conversation_history(phone_number, limit)


# Instancia global
message_processor = MessageProcessor()
