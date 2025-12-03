"""
Configuración centralizada de la aplicación
Carga variables de entorno y define configuraciones globales
"""

import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings"""

    # Información de la aplicación
    app_name: str = "Evolution WhatsApp AI Bot"
    version: str = "1.0.0"
    debug: bool = False
    auto_create_tables: bool = True

    cors_allow_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str | None = None

    # Evolution API
    evolution_api_url: str
    evolution_api_key: str
    evolution_instance: str = "ia-whatsapp"

    # Google AI
    google_api_key: str
    gemini_model: str = "gemini-lite-latest"
    gemini_temperature: float = 0.7

    # Serper (Google Search)
    serper_api_key: str | None = None

    # LangChain Agent
    memory_window_size: int = 10
    agent_max_iterations: int = 3
    agent_verbose: bool = True

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def supabase_key_final(self) -> str:
        """Retorna service_role_key si existe, sino el key normal"""
        return self.supabase_service_role_key or self.supabase_key

    @property
    def has_google_search(self) -> bool:
        """Verifica si Google Search está disponible"""
        return bool(self.serper_api_key)


# Instancia global de configuración
settings = Settings()


# Configuración de logging basada en settings

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
