"""
Servicios del proyecto
Expone los servicios principales para facilitar las importaciones
"""

from app.services.supabase_service import supabase_service
from app.services.evolution_service import evolution_service
from app.services.message_service import message_processor

__all__ = [
    "supabase_service",
    "evolution_service",
    "message_processor"
]
