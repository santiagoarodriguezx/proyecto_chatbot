"""
Cliente mínimo para Supabase usando `supabase` (supabase-py).

Provee `insert_row` y funciones utilitarias para `message_logs` y `prompts`.
Requiere las variables de entorno `SUPABASE_URL` y `SUPABASE_KEY`.
"""
from dotenv import load_dotenv
import os
from typing import Any, Dict, List

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Las variables SUPABASE_URL y SUPABASE_KEY (o SUPABASE_SERVICE_ROLE_KEY) deben estar configuradas"
    )

try:
    from supabase import create_client
except Exception as e:
    raise RuntimeError("Instala la dependencia 'supabase' (pip install supabase)") from e

_client = create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_row(table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inserta un registro en la tabla indicada y devuelve el resultado.
    Lanza excepción en caso de error para que el caller la maneje.
    """
    res = _client.table(table).insert(payload).execute()
    return {"status_code": getattr(res, "status_code", None), "data": getattr(res, "data", None)}


def select_all(table: str) -> List[Dict[str, Any]]:
    """Selecciona todos los registros de la tabla (útil para debug)."""
    res = _client.table(table).select("*").execute()
    return getattr(res, "data", res)


def fetch_recent_messages(limit: int = 20) -> List[Dict[str, Any]]:
    """Devuelve los registros más recientes de message_logs ordenados por id."""
    limit = max(1, min(limit, 100))
    res = (
        _client
        .table("message_logs")
        .select("*")
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )
    return getattr(res, "data", res)


def fetch_prompts(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los prompts almacenados ordenados por id descendente."""
    limit = max(1, min(limit, 100))
    res = (
        _client
        .table("prompts")
        .select("*")
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )
    return getattr(res, "data", res)

