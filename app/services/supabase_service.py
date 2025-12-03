"""
Supabase Service - Servicio para interactuar con Supabase
Maneja conversaciones, mensajes, respuestas de IA y prompts
"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from app.config.config import settings


SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key_final

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ Variables de Supabase no configuradas")
    _client = None
else:
    try:
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️ Error inicializando Supabase: {e}")
        _client = None


class SupabaseService:
    """Servicio para gestionar datos en Supabase"""

    def __init__(self):
        """Inicializar servicio de Supabase"""
        self.client = _client

    def is_available(self) -> bool:
        """Verificar si Supabase esta disponible"""
        return self.client is not None

    # ========== CONVERSACIONES ==========

    def get_or_create_conversation(self, phone_number: str, user_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtener conversacion existente o crear una nueva

        Args:
            phone_number: Numero de telefono del usuario
            user_name: Nombre del usuario (opcional)

        Returns:
            Datos de la conversacion o None si hay error
        """
        if not self.is_available():
            return None

        try:
            # Buscar conversacion existente
            res = self.client.table("conversations").select(
                "*").eq("phone_number", phone_number).execute()

            if res.data and len(res.data) > 0:
                # Actualizar last_message_at
                conversation = res.data[0]
                self.client.table("conversations").update({
                    "last_message_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", conversation["id"]).execute()
                return conversation
            else:
                # Crear nueva conversacion
                new_conversation = {
                    "phone_number": phone_number,
                    "user_name": user_name,
                    "current_state": "active",
                    "context": {},
                    "last_message_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                res = self.client.table("conversations").insert(
                    new_conversation).execute()
                return res.data[0] if res.data else None

        except Exception as e:
            print(f"❌ Error en get_or_create_conversation: {e}")
            return None

    def update_conversation_context(self, phone_number: str, context: Dict[str, Any]) -> bool:
        """
        Actualizar el contexto de una conversacion

        Args:
            phone_number: Numero de telefono
            context: Nuevo contexto a guardar

        Returns:
            True si se actualizo correctamente
        """
        if not self.is_available():
            return False

        try:
            self.client.table("conversations").update({
                "context": context,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("phone_number", phone_number).execute()
            return True
        except Exception as e:
            print(f"❌ Error actualizando contexto: {e}")
            return False

    # ========== MESSAGE LOGS ==========

    def save_message_log(
        self,
        phone_number: str,
        message_text: str,
        direction: str,
        status: str = "sent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Guardar un mensaje en los logs

        Args:
            phone_number: Numero de telefono
            message_text: Texto del mensaje
            direction: 'incoming' o 'outgoing'
            status: Estado del mensaje
            metadata: Metadatos adicionales

        Returns:
            Datos del mensaje guardado o None si hay error
        """
        if not self.is_available():
            return None

        try:
            message_log = {
                "phone_number": phone_number,
                "message_text": message_text,
                "direction": direction,
                "status": status,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            res = self.client.table("message_logs").insert(
                message_log).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"❌ Error guardando message_log: {e}")
            return None

    def get_conversation_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener historial de mensajes de una conversacion

        Args:
            phone_number: Numero de telefono
            limit: Cantidad de mensajes a obtener

        Returns:
            Lista de mensajes
        """
        if not self.is_available():
            return []

        try:
            res = self.client.table("message_logs")\
                .select("*")\
                .eq("phone_number", phone_number)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return []

    # ========== AI RESPONSES ==========

    def save_ai_response(
        self,
        message_log_id: Optional[int],
        response_text: str,
        prompt_used: Optional[str] = None,
        model_used: Optional[str] = "gemini-flash-lite-latest",
        tokens_used: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Guardar respuesta de IA

        Args:
            message_log_id: ID del mensaje asociado
            response_text: Texto de la respuesta
            prompt_used: Prompt utilizado
            model_used: Modelo de IA usado
            tokens_used: Tokens consumidos
            response_time_ms: Tiempo de respuesta en ms
            error_message: Mensaje de error si ocurrio

        Returns:
            Datos de la respuesta guardada o None si hay error
        """
        if not self.is_available():
            return None

        try:
            ai_response = {
                "message_log_id": message_log_id,
                "response_text": response_text,
                "prompt_used": prompt_used,
                "model_used": model_used,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms,
                "error_message": error_message,
                "created_at": datetime.utcnow().isoformat()
            }
            res = self.client.table("ai_responses").insert(
                ai_response).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"❌ Error guardando ai_response: {e}")
            return None

    # ========== PROMPTS ==========

    def get_active_prompt(self, name: str = "default") -> Optional[str]:
        """
        Obtener prompt activo por nombre

        Args:
            name: Nombre del prompt

        Returns:
            Contenido del prompt o None
        """
        if not self.is_available():
            return None

        try:
            res = self.client.table("prompts")\
                .select("content")\
                .eq("name", name)\
                .eq("is_active", True)\
                .execute()

            if res.data and len(res.data) > 0:
                return res.data[0]["content"]
            return None
        except Exception as e:
            print(f"❌ Error obteniendo prompt: {e}")
            return None

    def list_active_prompts(self) -> List[Dict[str, Any]]:
        """
        Listar todos los prompts activos

        Returns:
            Lista de prompts activos
        """
        if not self.is_available():
            return []

        try:
            res = self.client.table("prompts")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"❌ Error listando prompts: {e}")
            return []

    def create_or_update_prompt(
        self,
        name: str,
        content: str,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Crear o actualizar un prompt

        Args:
            name: Nombre del prompt
            content: Contenido del prompt
            description: Descripcion del prompt
            is_active: Si el prompt esta activo

        Returns:
            Datos del prompt creado/actualizado o None
        """
        if not self.is_available():
            return None

        try:
            # Verificar si existe
            res = self.client.table("prompts").select(
                "*").eq("name", name).execute()

            if res.data and len(res.data) > 0:
                # Actualizar
                prompt_data = {
                    "content": content,
                    "description": description,
                    "is_active": is_active,
                    "updated_at": datetime.utcnow().isoformat()
                }
                res = self.client.table("prompts").update(
                    prompt_data).eq("name", name).execute()
            else:
                # Crear
                prompt_data = {
                    "name": name,
                    "content": content,
                    "description": description,
                    "is_active": is_active,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                res = self.client.table("prompts").insert(
                    prompt_data).execute()

            return res.data[0] if res.data else None
        except Exception as e:
            print(f"❌ Error creando/actualizando prompt: {e}")
            return None


# Instancia global del servicio
supabase_service = SupabaseService()
