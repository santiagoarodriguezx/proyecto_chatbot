"""
Rutas de prompts
"""
from fastapi import APIRouter, HTTPException
from app.schemas.models import MessageResponse, PromptRequest
from app.services.database import insert_row, fetch_prompts
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=MessageResponse)
async def create_prompt(prompt: PromptRequest):
    """Crear un prompt"""
    if not insert_row:
        raise HTTPException(status_code=503, detail="Supabase no configurado")

    try:
        payload = prompt.model_dump()
        insert_result = insert_row("prompts", payload)
        stored_data = insert_result.get("data") if isinstance(
            insert_result, dict) else None
        return MessageResponse(success=True, message="Prompt guardado correctamente", data={"stored": stored_data or payload})
    except Exception as e:
        logger.error(f"Error guardando prompt: {e}")
        raise HTTPException(
            status_code=500, detail="No se pudo guardar el prompt")


@router.get("/", response_model=MessageResponse)
def list_prompts(limit: int = 20):
    """Listar prompts"""
    if not fetch_prompts:
        raise HTTPException(status_code=503, detail="Supabase no configurado")

    try:
        data = fetch_prompts(limit)
        return MessageResponse(success=True, message="Prompts recuperados", data={"count": len(data), "items": data})
    except Exception as e:
        logger.error(f"Error listando prompts: {e}")
        raise HTTPException(
            status_code=500, detail="No se pudieron obtener los prompts")
