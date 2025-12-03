"""
Rutas de analytics
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.schemas.models import MessageResponse
from app.services.database import _client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary", response_model=MessageResponse)
def get_analytics_summary(days: int = 7):
    """Resumen de analytics"""
    try:
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        messages = _client.table("message_logs").select(
            "*", count="exact").gte("created_at", start_date).execute()
        incoming = _client.table("message_logs").select(
            "*", count="exact").eq("direction", "incoming").gte("created_at", start_date).execute()
        outgoing = _client.table("message_logs").select(
            "*", count="exact").eq("direction", "outgoing").gte("created_at", start_date).execute()
        unique_users = _client.table("message_logs").select(
            "phone_number").gte("created_at", start_date).execute()
        unique_count = len(set(m["phone_number"] for m in unique_users.data))

        return MessageResponse(
            success=True,
            message="Analytics recuperados",
            data={
                "period_days": days,
                "total_messages": messages.count,
                "incoming_messages": incoming.count,
                "outgoing_messages": outgoing.count,
                "unique_users": unique_count
            }
        )
    except Exception as e:
        logger.error(f"Error en analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
