"""
Rutas de prompts
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import MessageResponse, PromptRequest
from app.services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=MessageResponse)
async def create_prompt(prompt: PromptRequest):
    """Crear un prompt"""
    if not supabase_service.is_available():
        raise HTTPException(status_code=503, detail="Supabase no configurado")

    try:
        payload = prompt.model_dump()
        result = supabase_service.create_or_update_prompt(
            name=payload.get("name"),
            content=payload.get("content"),
            description=payload.get("description"),
            is_active=payload.get("is_active", True)
        )
        return MessageResponse(success=True, message="Prompt guardado correctamente", data={"stored": result})
    except Exception as e:
        logger.error(f"Error guardando prompt: {e}")
        raise HTTPException(
            status_code=500, detail="No se pudo guardar el prompt")


@router.get("/", response_model=MessageResponse)
def list_prompts(active_only: bool = False):
    """Listar prompts"""
    if not supabase_service.is_available():
        raise HTTPException(status_code=503, detail="Supabase no configurado")

    try:
        if active_only:
            data = supabase_service.list_active_prompts()
        else:
            client = supabase_service.client
            result = client.table("prompts").select("*").execute()
            data = result.data if result.data else []

        return MessageResponse(success=True, message="Prompts recuperados", data={"count": len(data), "items": data})
    except Exception as e:
        logger.error(f"Error listando prompts: {e}")
        raise HTTPException(
            status_code=500, detail="No se pudieron obtener los prompts")
