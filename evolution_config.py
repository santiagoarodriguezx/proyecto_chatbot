"""
Configuración para Evolution API
Archivo de configuración centralizado para la integración con Evolution API
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class EvolutionConfig:
    """Configuración para Evolution API"""

    # URL de tu Evolution API en AWS
    API_URL = os.getenv("EVOLUTION_API_URL")

    # API Key de tu Evolution API
    API_KEY = os.getenv("EVOLUTION_API_KEY")

    # Nombre de la instancia
    INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE", "asd")

    # URL de tu bot (la que expusiste con ngrok o tu IP pública)
    WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL")

    # Timeout para requests HTTP (en segundos)
    REQUEST_TIMEOUT = 30

    # Configuración de reintentos
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos entre reintentos

    @staticmethod
    def get_headers():
        return {
            "Content-Type": "application/json",
            "apikey": EvolutionConfig.API_KEY
        }

    @staticmethod
    def get_instance_url(endpoint=""):
        api_url = EvolutionConfig.API_URL.rstrip('/')
        return f"{api_url}/{endpoint}/{EvolutionConfig.INSTANCE_NAME}" if endpoint else f"{api_url}/{EvolutionConfig.INSTANCE_NAME}"

    @staticmethod
    def get_send_text_url():
        """URL para enviar mensajes de texto"""
        api_url = EvolutionConfig.API_URL.rstrip('/')
        return f"{api_url}/message/sendText/{EvolutionConfig.INSTANCE_NAME}"

    @staticmethod
    def get_send_media_url():
        """URL para enviar archivos multimedia"""
        api_url = EvolutionConfig.API_URL.rstrip('/')
        return f"{api_url}/message/sendMedia/{EvolutionConfig.INSTANCE_NAME}"

    @staticmethod
    def get_instance_status_url():
        """URL para consultar estado de la instancia"""
        api_url = EvolutionConfig.API_URL.rstrip('/')
        return f"{api_url}/instance/connectionState/{EvolutionConfig.INSTANCE_NAME}"


evolution_config = EvolutionConfig()
