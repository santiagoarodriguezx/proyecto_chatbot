"""
Servicio de IA - Wrapper para Google Generative AI
Maneja toda la comunicación con Google Generative AI
"""

import logging
from typing import Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar .env desde el mismo directorio
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


class GoogleGenerativeAIWrapper:
    """Wrapper para Google Generative AI con manejo de múltiples API keys"""

    # ✅ Variable de clase compartida entre TODAS las instancias
    _shared_usage = None

    def __init__(self, temperature: float = 0.1, max_output_tokens: int = 1024):
        """
        Inicializar wrapper de Google Generative AI

        Args:
            temperature: Temperatura para la generación (0.0 - 1.0)
            max_output_tokens: Máximo número de tokens en la respuesta
        """
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._last_usage = None  # Almacenar info de tokens del último llamado

        # La configuración global de la API key se realiza arriba leyendo GENAI_API_KEY_1 desde .env

    def get_last_usage(self) -> Optional[dict]:
        """Obtener información de tokens del último llamado (de cualquier instancia)"""
        # ✅ Retornar usage compartido entre todas las instancias
        return GoogleGenerativeAIWrapper._shared_usage

    @property
    def _llm_type(self) -> str:
        return "google_generative_ai"

    def _call(self, prompt: str, **kwargs) -> str:
        """
        Llamada sincrónica a Google Generative AI

        Args:
            prompt: Texto del prompt
            **kwargs: Argumentos adicionales

        Returns:
            Respuesta generada por la IA
        """
        try:
            # Crear el modelo
            model = genai.GenerativeModel(
                "gemini-2.5-flash-lite",
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                )
            )

            # Realizar la llamada
            response = model.generate_content(prompt)

            # Extraer información de tokens directamente de la respuesta
            usage_metadata = None
            if hasattr(response, 'usage_metadata'):
                usage_metadata = {
                    'prompt_tokens': response.usage_metadata.prompt_token_count,
                    'completion_tokens': response.usage_metadata.candidates_token_count,
                    'total_tokens': response.usage_metadata.total_token_count
                }

            # Verificar si hay contenido válido
            if hasattr(response, 'text') and response.text:
                # Almacenar metadata en instancia Y en variable compartida
                self._last_usage = usage_metadata
                GoogleGenerativeAIWrapper._shared_usage = usage_metadata
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    # Almacenar metadata en instancia Y en variable compartida
                    self._last_usage = usage_metadata
                    GoogleGenerativeAIWrapper._shared_usage = usage_metadata
                    return candidate.content.parts[0].text

            # Verificar finish_reason si no hay contenido
            if hasattr(response, 'candidates') and response.candidates:
                finish_reason = response.candidates[0].finish_reason
                if finish_reason == 2:  # SAFETY
                    return "El contenido fue filtrado por políticas de seguridad."
                elif finish_reason == 3:  # RECITATION
                    return "El contenido fue filtrado por derechos de autor."
                elif finish_reason == 4:  # OTHER
                    return "El contenido fue filtrado por otras razones."

            # Si no hay texto válido, considerar como error
            raise Exception("Respuesta sin contenido válido")

        except Exception as e:
            logger.error(f"Error al generar respuesta: {str(e)}")
            return "Lo siento, no puedo procesar tu solicitud en este momento. Por favor intenta más tarde. 😅"

    async def _acall(self, prompt: str, **kwargs: Any) -> str:
        """Llamada asincrónica (usa la sincrónica internamente)"""
        return self._call(prompt)

    def predict(self, prompt: str, **kwargs: Any) -> str:
        """Método de compatibilidad"""
        return self._call(prompt)


class AIService:
    """Servicio principal de IA que coordina todos los modelos"""

    def __init__(self):
        """Inicializar servicio de IA"""
        self.llm = GoogleGenerativeAIWrapper()

    def generate_response(self, prompt: str, temperature: float = 0.1, max_tokens: int = 1024) -> str:
        """
        Generar respuesta usando IA

        Args:
            prompt: Texto del prompt
            temperature: Temperatura para la generación
            max_tokens: Máximo número de tokens

        Returns:
            Respuesta generada
        """
        # Crear instancia con parámetros específicos si es necesario
        if temperature != 0.1 or max_tokens != 1024:
            llm = GoogleGenerativeAIWrapper(
                temperature=temperature, max_output_tokens=max_tokens)
            return llm._call(prompt)

        return self.llm._call(prompt)


# Instancia global del servicio de IA
ai_service = AIService()
